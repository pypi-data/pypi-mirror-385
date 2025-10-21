#
# Cerebras implementation of NAdam optimizer. Adapted from the `torch.optim.NAdam` implementation.
#
# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause
#

from typing import Tuple

import torch

import cerebras.pytorch as cstorch

from .optimizer import Optimizer, ParamsT


class NAdam(Optimizer):
    r"""Implements NAdam algorithm to execute within the constraints
    of the Cerebras WSE, including pre-initializing optimizer state.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float, optional): learning rate (default: 2e-3)
        betas (Tuple[float, float], optional): coefficients used for computing
            running averages of gradient and its square (default: (0.9, 0.999))
        eps (float, optional): term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0)
        momentum_decay (float, optional): momentum momentum_decay (default: 4e-3)
        foreach (bool, optional): whether foreach implementation of optimizer
            is used (default: None)

    For further details regarding the algorithm refer to
    Incorporating Nesterov Momentum into Adam:
    https://openreview.net/forum?id=OM0jvwB8jIp57ZJjtNEZ
    """

    def __init__(
        self,
        params: ParamsT,
        lr: float = 2e-3,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0,
        momentum_decay: float = 4e-3,
    ):
        if lr < 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        if eps < 0.0:
            raise ValueError(f"Invalid epsilon value: {eps}")
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 0: {betas[0]}")
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 1: {betas[1]}")
        if weight_decay < 0.0:
            raise ValueError(f"Invalid weight_decay value: {weight_decay}")
        if momentum_decay < 0.0:
            raise ValueError(f"Invalid momentum_decay value: {momentum_decay}")

        defaults = dict(
            lr=lr,
            betas=betas,
            eps=eps,
            weight_decay=weight_decay,
            momentum_decay=momentum_decay,
        )
        super().__init__(params, defaults, enable_global_step=True)

    def preinitialize(self):
        """Allocates tensors for the optimizer state to allow direct compilation
        of the model before the first step.
        """
        for group in self.param_groups:
            for p in group['params']:
                self.state[p]["mu_product"] = torch.tensor(1.0).to(p.device)
                self.state[p]["exp_avg"] = cstorch.zeros_like(p)
                self.state[p]["exp_avg_sq"] = cstorch.zeros_like(p)

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step.

        Args:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            weight_decay = group["weight_decay"]
            beta1, beta2 = group["betas"]
            if not isinstance(beta2, torch.Tensor):
                beta2 = torch.tensor(beta2)
            momentum_decay = group["momentum_decay"]
            eps = group["eps"]
            lr = group["lr"]
            for p in group['params']:
                if p.grad is not None:
                    if p.grad.is_sparse:
                        raise RuntimeError(
                            'NAdam does not support sparse gradients'
                        )

                    state = self.state[p]
                    exp_avg = state["exp_avg"]
                    exp_avg_sq = state["exp_avg_sq"]
                    mu_product = state["mu_product"]
                    global_step = self.increment_global_step(p)

                    beta2t = torch.pow(beta2.to(p.device), global_step)
                    bias_correction2 = 1 - beta2t

                    grad = p.grad

                    grad = grad + p * weight_decay

                    # calculate the momentum cache \mu^{t} and \mu^{t+1}
                    point_nine_six = torch.tensor(0.96).to(p.device)
                    mu_pow = torch.pow(
                        point_nine_six, (global_step * momentum_decay)
                    )
                    mu = beta1 * (1.0 - 0.5 * (mu_pow))
                    mu_next_pow = torch.pow(
                        point_nine_six,
                        ((global_step + 1) * momentum_decay),
                    )
                    mu_next = beta1 * (1.0 - 0.5 * (mu_next_pow))

                    # update the mu_product
                    mu_product *= mu
                    mu_product_next = mu_product * mu * mu_next

                    # decay the first and second moment running average coefficient
                    exp_avg.mul_(beta1).add_(grad, alpha=1.0 - beta1)
                    exp_avg_sq.mul_(beta2).addcmul_(
                        grad, grad, value=1.0 - beta2
                    )

                    # denom of the update step
                    denom = exp_avg_sq.div(bias_correction2).sqrt().add_(eps)
                    # num of the update step without lr
                    momentum_update = (mu_next * exp_avg) / (
                        1.0 - mu_product_next
                    )
                    grad_update = (grad * (1.0 - mu)) / (1.0 - mu_product)
                    update = momentum_update + grad_update
                    # multiply with lr
                    update *= -lr
                    # update params
                    p.addcdiv_(update, denom)

        return loss
