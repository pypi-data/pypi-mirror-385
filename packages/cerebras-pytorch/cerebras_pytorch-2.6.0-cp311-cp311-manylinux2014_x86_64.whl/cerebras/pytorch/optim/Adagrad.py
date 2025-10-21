# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""contains the Cerebras Adagrad implementation."""
import torch

import cerebras.pytorch as cstorch

from .optimizer import Optimizer, ParamsT


class Adagrad(Optimizer):
    r"""Adagrad optimizer implemented to conform to execution within the
    constraints of the Cerebras WSE.

    Args:
        params: iterable of parameters to optimize or dicts defining parameter groups
        lr: learning rate
        lr_decay: learning rate decay
        weight_decay: weight decay (L2 penalty)
        eps: term added to the denominator to improve numerical stability
        maximize: maximize the params based on the objective instead of minimizing

    Adaptive Subgradient Methods for Online Learning and Stochastic
    Optimization: http://jmlr.org/papers/v12/duchi11a.html

    """

    def __init__(
        self,
        params: ParamsT,
        lr: float = 1e-2,
        lr_decay: float = 0,
        weight_decay: float = 0,
        initial_accumulator_value: float = 0,
        eps: float = 1e-6,
        maximize: bool = False,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if lr_decay < 0.0:
            raise ValueError("Invalid lr_decay value: {}".format(lr_decay))
        if weight_decay < 0.0:
            raise ValueError(
                "Invalid weight_decay value: {}".format(weight_decay)
            )
        if initial_accumulator_value < 0.0:
            raise ValueError(
                "Invalid initial_accumulator_value value: {}".format(
                    initial_accumulator_value
                )
            )
        if eps < 0.0:
            raise ValueError("Invalid epsilon value: {}".format(eps))

        defaults = dict(
            lr=lr,
            lr_decay=lr_decay,
            eps=eps,
            weight_decay=weight_decay,
            initial_accumulator_value=initial_accumulator_value,
            maximize=maximize,
        )
        super().__init__(params, defaults, enable_global_step=True)

    def preinitialize(self):
        """
        Allocates tensors for the optimizer state to allow direct compilation
        of the model before the first step.
        """
        for group in self.param_groups:
            for p in group['params']:
                self.state[p]["sum"] = cstorch.full_like(
                    p,
                    group["initial_accumulator_value"],
                )

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step.

        Args:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            lr = group["lr"]
            weight_decay = group["weight_decay"]
            lr_decay = group["lr_decay"]
            eps = group["eps"]
            maximize = group["maximize"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad

                if grad.is_sparse:
                    raise RuntimeError(
                        "Adagrad does not support sparse gradients."
                    )

                state = self.state[p]
                state_sum = state["sum"]

                global_step = self.increment_global_step(p)

                grad = grad if not maximize else -grad

                grad = grad + p * weight_decay

                state_sum.addcmul_(grad, grad, value=1.0)
                std = state_sum.sqrt().add_(eps)

                # BEGIN_CEREBRAS_ONLY
                # The following two lines implements clr, in two steps:
                # clr = lr / (1.0 + (global_step - 1.0) * lr_decay)
                # This workaround avoids LR constant folding?
                # END_CEREBRAS_ONLY
                grad.div_(1.0 + (global_step - 1.0) * lr_decay)
                p.addcdiv_(-lr * grad, std)

        return loss
