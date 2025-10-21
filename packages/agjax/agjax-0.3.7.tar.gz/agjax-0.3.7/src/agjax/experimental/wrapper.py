"""Defines a jax wrapper for autograd-differentiable functions.

Copyright (c) 2025 invrs.io LLC
"""

import functools
from packaging import version
from typing import Any, Callable, List, Tuple, Union

import autograd  # type: ignore[import-untyped]
import jax
import jax.numpy as jnp
import numpy as onp

from agjax import utils

if version.Version(jax.__version__) > version.Version("0.4.31"):
    callback_sequential = functools.partial(jax.pure_callback, vmap_method="sequential")
else:
    callback_sequential = functools.partial(jax.pure_callback, vectorized=False)

_FORWARD_STAGE = "fwd"
_BACKWARD_STAGE = "bwd"


def wrap_for_jax(
    fn: Callable[[Any], Any],
    result_shape_dtypes: Any,
    nondiff_argnums: Union[int, Tuple[int, ...]] = (),
    nondiff_outputnums: Union[int, Tuple[int, ...]] = (),
) -> Callable[[Any], Any]:
    """Wraps `fn` so that it can be differentiated by jax.

    The wrapped function is suitable for jax transformations such as `grad`, `jit`,
    `vmap`, and `jacrev`, which is achieved using `jax.pure_callback`.

    Arguments to `fn` must be convertible to jax types, as must all outputs. The
    arguments to the wrapped function should be jax types, and the outputs will be
    jax types.

    Arguments which need not be differentiated with respect to may be specified in
    `nondiff_argnums`, while outputs that need not be differentiated may be specified
    in `nondiff_outputnums`.

    Args:
        fn: The autograd-differentiable function.
        result_shape_dtypes: A pytree matching the jax-converted output of `fn`.
            Specifically, the pytree structure, leaf shapes, and datatypes must match.
        nondiff_argnums: The arguments that cannot be differentiated with respect to.
        nondiff_outputnums: The outputs that cannot be differentiated.

    Returns:
        The wrapped function.
    """
    _nondiff_argnums, _ = utils.ensure_tuple(nondiff_argnums)
    _nondiff_outputnums, _ = utils.ensure_tuple(nondiff_outputnums)
    del nondiff_argnums, nondiff_outputnums

    split_args_fn = functools.partial(utils.split, idx=_nondiff_argnums)
    merge_args_fn = functools.partial(utils.merge, idx=_nondiff_argnums)
    split_outputs_fn = functools.partial(utils.split, idx=_nondiff_outputnums)
    merge_outputs_fn = functools.partial(utils.merge, idx=_nondiff_outputnums)

    # Vjp functions created in the "forward stage" of the calculation, and stored in
    # the `vjp_fns` list. When the calculation switches from the backward to the
    # forward stage, the list of vjp functions is cleared.
    stage = _FORWARD_STAGE
    vjp_fns: List[Callable[[Any], Any]] = []

    @jax.custom_vjp  # type: ignore[misc]
    def _fn(*args: Any) -> Any:
        utils.validate_nondiff_argnums_for_args(_nondiff_argnums, args)
        outputs = callback_sequential(
            lambda *args: fn(*utils.to_numpy(args)),
            result_shape_dtypes,
            *args,
        )
        utils.validate_nondiff_outputnums_for_outputs(_nondiff_outputnums, outputs)
        return outputs

    def _fwd_fn(*args: Any) -> Any:
        def make_vjp(*args: Any) -> Any:
            args = utils.to_numpy(args)
            nonlocal stage
            if stage == _BACKWARD_STAGE:
                vjp_fns.clear()
            stage = _FORWARD_STAGE

            # Variables updated nonlocally where `fn` is evaluated.
            is_tuple_outputs: bool = None  # type: ignore[assignment]
            nondiff_outputs: Tuple[Any, ...] = None  # type: ignore[assignment]
            diff_outputs_treedef: Any = None

            def _tuple_fn(*args: Any) -> onp.ndarray:
                nonlocal is_tuple_outputs
                nonlocal nondiff_outputs
                nonlocal diff_outputs_treedef

                utils.validate_nondiff_argnums_for_args(_nondiff_argnums, args)
                outputs = fn(*args)
                utils.validate_nondiff_outputnums_for_outputs(
                    _nondiff_outputnums, outputs
                )

                outputs, is_tuple_outputs = utils.ensure_tuple(outputs)
                nondiff_outputs, diff_outputs = split_outputs_fn(outputs)
                nondiff_outputs = utils.arraybox_to_numpy(nondiff_outputs)
                diff_outputs_leaves, diff_outputs_treedef = utils.tree_flatten(
                    diff_outputs
                )
                return autograd.builtins.tuple(tuple(diff_outputs_leaves))

            args = utils.to_numpy(args)
            diff_argnums = tuple(
                i for i in range(len(args)) if i not in _nondiff_argnums
            )
            tuple_vjp_fn, diff_outputs_leaves = autograd.make_vjp(
                _tuple_fn, argnum=diff_argnums
            )(*args)
            diff_outputs = utils.tree_unflatten(
                diff_outputs_treedef, diff_outputs_leaves
            )
            outputs = merge_outputs_fn(nondiff_outputs, diff_outputs)
            outputs = outputs if is_tuple_outputs else outputs[0]

            def _vjp_fn(*diff_outputs: Any) -> Any:
                diff_outputs_leaves = utils.tree_leaves(diff_outputs)
                grad = tuple_vjp_fn(utils.to_numpy(diff_outputs_leaves))
                return grad

            key = len(vjp_fns)
            vjp_fns.append(_vjp_fn)
            return outputs, key

        outputs, key = callback_sequential(
            make_vjp,
            (result_shape_dtypes, jnp.asarray(0)),
            *args,
        )
        return outputs, (args, key)

    def _bwd_fn(*bwd_args: Any) -> Any:
        def _pure_fn(key: jnp.ndarray, tangents: Tuple[Any, ...]) -> Any:
            tangents = utils.to_numpy(tangents)
            nonlocal stage
            stage = _BACKWARD_STAGE
            vjp_fn = vjp_fns[int(onp.asarray(key))]
            return vjp_fn(*tangents)

        (args, key), *tangents = bwd_args
        _, diff_args = split_args_fn(args)
        result_shape_dtypes = utils.to_jax(diff_args)
        grads = callback_sequential(
            _pure_fn,
            result_shape_dtypes,
            key,
            tangents,
        )
        return merge_args_fn([None] * len(_nondiff_argnums), grads)

    _fn.defvjp(_fwd_fn, _bwd_fn)

    return _fn  # type: ignore[no-any-return]
