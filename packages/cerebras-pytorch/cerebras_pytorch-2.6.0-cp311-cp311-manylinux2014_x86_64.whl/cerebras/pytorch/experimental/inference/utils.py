# Copyright 2016-2024 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

import functools
from typing import Callable

import torch

import cerebras.pytorch as cstorch
import cerebras.pytorch.nn.functional as F
from cerebras.pytorch.lib import cerebras_pytorch_lib


def hoist_function(func: Callable) -> Callable:
    """Decorator to add hints for compiler to hoist function.

    Name of the hoisted function should be unique. Nested hoisting is not
    allowed. The checks are not thread-safe but it is okay as tracing is not
    multithreaded.
    """
    magic_str = f"FUNC_{func.__name__}"
    if magic_str in hoist_function.hoisted:
        raise ValueError(
            f"There is already a hoisted function of the same name '{func.__name__}'."
        )
    hoist_function.hoisted.add(magic_str)

    def collect_tensors(args, kwargs):
        tensors = []

        def append_tensor(arg):
            if isinstance(arg, torch.Tensor):
                tensors.append(arg)
            return arg

        torch.utils._pytree.tree_map(append_tensor, (args, kwargs))
        return tensors

    def map_tensors(tensors, replacements, args, kwargs):
        d = dict(zip(tensors, replacements))

        def map_fn(arg):
            if isinstance(arg, torch.Tensor):
                return d.get(arg, arg)
            return arg

        return torch.utils._pytree.tree_map(map_fn, (args, kwargs))

    def enter_scope(*args, **kwargs):
        if not cstorch.use_cs():
            return args, kwargs

        tensors = collect_tensors(args, kwargs)
        replacements = cstorch.cirh.ScopeBoundary(
            tensors, boundary_type=F.BEGIN_FORWARD, scope_name=magic_str
        )

        return map_tensors(tensors, replacements, args, kwargs)

    def exit_scope(args):
        if not cstorch.use_cs():
            return args

        tensors = collect_tensors(args, {})
        replacements = cstorch.cirh.ScopeBoundary(
            tensors, boundary_type=F.END_FORWARD, scope_name=magic_str
        )

        args, _ = map_tensors(tensors, replacements, args, {})
        return args

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if hoist_function.hoisting is not None:
            raise ValueError(
                f"Nested hoisting of '{func.__name__}' under '{hoist_function.hoisting}' is not allowed."
            )

        hoist_function.hoisting = func.__name__
        args, kwargs = enter_scope(*args, **kwargs)
        results = exit_scope(func(*args, **kwargs))
        hoist_function.hoisting = None
        return results

    return wrapper


hoist_function.hoisted = set()  # Set of hoisted function names.
hoist_function.hoisting = None  # Current function begin hoisted.


def register_weight(tensor: torch.Tensor):
    """
    Forcing ws_km.load_input for weights.
    """
    cerebras_pytorch_lib.set_attribute(tensor, "cs.static_input", True)


def register_state(tensor: torch.Tensor):
    """
    Forcing ws_km.load_state for nn.Module buffer.
    """
    cerebras_pytorch_lib.set_attribute(tensor, "cs.state_buffer", True)
