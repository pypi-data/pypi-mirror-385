"""Functions related transforming to and from the Fourier basis.

Copyright (c) 2025 invrs.io LLC
"""

from typing import Tuple

import jax.numpy as jnp

from fmmax import basis, utils
from fmmax._fft import _standard_toeplitz_indices


def fourier_convolution_matrix(
    x: jnp.ndarray,
    expansion: basis.Expansion,
) -> jnp.ndarray:
    """Computes the Fourier convolution matrix for ``x`` and ``basis_coefficients``.

    The Fourier convolution matrix at location ``(i, j)`` gives the Fourier
    coefficient associated with the lattice vector obtained by subtracting the
    ``j``th reciprocal lattice vector from the ``i``th reciprocal lattice basis.
    See equation 8 from [2012 Liu].

    Args:
        x: The array for which the Fourier coefficients are sought.
        expansion: The field expansion to be used.

    Returns:
        The coefficients, with shape ``(num_vectors, num_vectors)``.
    """
    basis.validate_shape_for_expansion(x.shape, expansion)

    x_fft = _fft2(x, axes=(-2, -1), norm="backward", centered_coordinates=True)
    x_fft /= jnp.prod(jnp.asarray(x.shape[-2:])).astype(x.dtype)
    idx = _standard_toeplitz_indices(expansion)
    return x_fft[..., idx[..., 0], idx[..., 1]]


def fft(
    x: jnp.ndarray,
    expansion: basis.Expansion,
    axes: Tuple[int, int] = (-2, -1),
    centered_coordinates: bool = True,
) -> jnp.ndarray:
    """Returns the 2D Fourier transform of ``x``.

    Args:
        x: The array to be transformed.
        expansion: The field expansion to be used.
        axes: The axes to be transformed, with default ``(-2, -1)``.
        centered_coordinates: Specifies the relationship between the physical
            coordinates and the indices of array elements in ``x``. If ``True``, the
            coordinates lie in the center of elements, so that the element with index
            ``(0, 0)`` lies at position ``du / 2 + dv / 2``. When ``False``, the
            coordinates lie in the corners of the elements, so that the ``(0, 0)``
            element lies at position ``0``.

    Returns:
        The transformed ``x``.
    """
    axes: Tuple[int, int] = utils.absolute_axes(axes, x.ndim)  # type: ignore[no-redef]
    basis.validate_shape_for_expansion(tuple([x.shape[ax] for ax in axes]), expansion)

    x_fft = _fft2(
        x,
        axes=axes,
        norm="forward",
        centered_coordinates=centered_coordinates,
    )

    leading_dims = len(x.shape[: axes[0]])
    trailing_dims = len(x.shape[axes[1] + 1 :])
    slices = (
        [slice(None)] * leading_dims
        + [expansion.basis_coefficients[:, 0], expansion.basis_coefficients[:, 1]]
        + [slice(None)] * trailing_dims
    )
    return x_fft[tuple(slices)]


def ifft(
    y: jnp.ndarray,
    expansion: basis.Expansion,
    shape: Tuple[int, int],
    axis: int = -1,
    centered_coordinates: bool = True,
) -> jnp.ndarray:
    """Returns the 2D inverse Fourier transform of ``y``.

    Args:
        y: The array to be transformed.
        expansion: The field expansion to be used.
        shape: The desired shape of the output array.
        axis: The axis containing the Fourier coefficients. Default is ``-1``, the
            final axis.
        centered_coordinates: Specifies the relationship between the physical
            coordinates and the indices of array elements in ``x``. If ``True``, the
            coordinates lie in the center of elements, so that the element with index
            ``(0, 0)`` lies at position ``du / 2 + dv / 2``. When ``False``, the
            coordinates lie in the corners of the elements, so that the ``(0, 0)``
            element lies at position ``0``.

    Returns:
        The inverse transformed ``y``.
    """
    (axis,) = utils.absolute_axes((axis,), y.ndim)
    assert y.shape[axis] == expansion.basis_coefficients.shape[-2]
    x_shape = y.shape[:axis] + shape + y.shape[axis + 1 :]
    assert len(x_shape) == y.ndim + 1

    basis.validate_shape_for_expansion(shape, expansion)

    leading_dims = len(y.shape[:axis])
    trailing_dims = len(y.shape[axis + 1 :])
    slices = (
        [slice(None)] * leading_dims
        + [expansion.basis_coefficients[:, 0], expansion.basis_coefficients[:, 1]]
        + [slice(None)] * trailing_dims
    )

    x = jnp.zeros(x_shape, y.dtype)
    x = x.at[tuple(slices)].set(y)
    return _ifft2(
        x,
        axes=(leading_dims, leading_dims + 1),
        norm="forward",
        centered_coordinates=centered_coordinates,
    )


def _fft2(
    x: jnp.ndarray,
    axes: Tuple[int, int] = (-2, -1),
    norm: str = "forward",
    centered_coordinates: bool = True,
) -> jnp.ndarray:
    """Two-dimensional Fourier transform."""
    y = jnp.fft.fft2(x, axes=axes, norm=norm)
    if centered_coordinates:
        axes = utils.absolute_axes(axes, ndim=x.ndim)  # type: ignore[assignment]
        ki = 0.5 * jnp.fft.fftfreq(x.shape[axes[0]], dtype=jnp.float32)[:, jnp.newaxis]
        kj = 0.5 * jnp.fft.fftfreq(x.shape[axes[1]], dtype=jnp.float32)[jnp.newaxis, :]
        phase = jnp.exp(-1j * 2 * jnp.pi * (ki + kj))
        phase = phase.reshape(phase.shape + (1,) * (x.ndim - axes[1] - 1))
        y = y * phase
    assert y.dtype == jnp.promote_types(x.dtype, jnp.complex64)
    return y


def _ifft2(
    x: jnp.ndarray,
    axes: Tuple[int, int] = (-2, -1),
    norm: str = "forward",
    centered_coordinates: bool = True,
) -> jnp.ndarray:
    """Two-dimensional inverse Fourier transform."""
    if centered_coordinates:
        axes = utils.absolute_axes(axes, ndim=x.ndim)  # type: ignore[assignment]
        ki = 0.5 * jnp.fft.fftfreq(x.shape[axes[0]], dtype=jnp.float32)[:, jnp.newaxis]
        kj = 0.5 * jnp.fft.fftfreq(x.shape[axes[1]], dtype=jnp.float32)[jnp.newaxis, :]
        phase = jnp.exp(1j * 2 * jnp.pi * (ki + kj))
        phase = phase.reshape(phase.shape + (1,) * (x.ndim - axes[1] - 1))
        x = x * phase
        assert x.dtype == jnp.promote_types(x.dtype, jnp.complex64)

    return jnp.fft.ifft2(x, axes=axes, norm=norm)
