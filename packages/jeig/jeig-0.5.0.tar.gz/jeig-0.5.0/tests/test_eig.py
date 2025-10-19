"""Tests for jax-wrapped eigendecomposition.

Copyright (c) 2025 invrs.io LLC
"""

import itertools
import unittest

import jax
import jax.numpy as jnp
import numpy as onp
from parameterized import parameterized

import jeig
from jeig import jeig as _jeig

jax.config.update("jax_enable_x64", True)


BACKENDS = [
    jeig.EigBackend.LAPACK,
    jeig.EigBackend.NUMPY,
    jeig.EigBackend.SCIPY,
    jeig.EigBackend.TORCH,
]

# Only test the cusolver backend if supported by the installed jax version.
if _jeig._SUPPORTS_CUSOLVER and jax.devices()[0].platform == "gpu":
    BACKENDS.append(jeig.EigBackend.CUSOLVER)

# Only test the magma backend if supported by the installed jax and torch versions.
if _jeig._SUPPORTS_MAGMA:
    BACKENDS.append(jeig.EigBackend.MAGMA)


SHAPES = [(1, 2, 2), (1, 16, 16), (2, 16, 16), (2, 64, 64)]


def _match_eigs(eigval, eigvec, reference_eigval, reference_eigvec):
    """Sorts eigenvalues/eigenvectors and enforces a phase convention."""
    delta = reference_eigval[..., jnp.newaxis] - eigval[..., jnp.newaxis, :]
    error = jnp.abs(delta)
    idx = onp.argmin(error, axis=-1)

    sorted_eigval = jnp.take_along_axis(eigval, idx, axis=-1)
    sorted_eigvec = jnp.take_along_axis(eigvec, idx[..., jnp.newaxis, :], axis=-1)

    # Align the phase of the eigenvectors to those of the reference.
    max_ind = jnp.argmax(jnp.abs(sorted_eigvec), axis=-2)
    max_component = jnp.take_along_axis(
        sorted_eigvec, max_ind[..., jnp.newaxis, :], axis=-2
    )
    reference_max_component = jnp.take_along_axis(
        reference_eigvec, max_ind[..., jnp.newaxis, :], axis=-2
    )
    sorted_eigvec *= jnp.exp(
        1j * (jnp.angle(max_component) - jnp.angle(reference_max_component))
    )

    assert eigvec.shape == sorted_eigvec.shape
    return sorted_eigval, sorted_eigvec


class BackendComparisonTest(unittest.TestCase):
    @parameterized.expand(itertools.product(BACKENDS, SHAPES))
    def test_backends_against_jax_symmetric_real(self, backend, shape):
        matrix = jax.random.normal(jax.random.PRNGKey(0), shape)
        matrix = 0.5 * (matrix + jnp.swapaxes(matrix, -1, -2))

        expected_eigval, expected_eigvec = jeig.eig(
            matrix, backend=jeig.EigBackend.LAPACK
        )
        eigval, eigvec = jeig.eig(matrix, backend=backend)
        eigval, eigvec = _match_eigs(eigval, eigvec, expected_eigval, expected_eigvec)

        onp.testing.assert_allclose(eigval, expected_eigval, err_msg=(backend, shape))
        onp.testing.assert_allclose(eigvec, expected_eigvec, err_msg=(backend, shape))

    @parameterized.expand(itertools.product(BACKENDS, SHAPES))
    def test_backends_against_jax_real(self, backend, shape):
        matrix = jax.random.normal(jax.random.PRNGKey(0), shape)

        expected_eigval, expected_eigvec = jeig.eig(
            matrix, backend=jeig.EigBackend.LAPACK
        )
        eigval, eigvec = jeig.eig(matrix, backend=backend)
        eigval, eigvec = _match_eigs(eigval, eigvec, expected_eigval, expected_eigvec)

        onp.testing.assert_allclose(eigval, expected_eigval, err_msg=(backend, shape))
        onp.testing.assert_allclose(eigvec, expected_eigvec, err_msg=(backend, shape))

    @parameterized.expand(itertools.product(BACKENDS, SHAPES))
    def test_backends_against_jax_complex(self, backend, shape):
        real, imag = jax.random.normal(jax.random.PRNGKey(0), (2,) + shape)
        matrix = real + 1j * imag

        expected_eigval, expected_eigvec = jeig.eig(
            matrix, backend=jeig.EigBackend.LAPACK
        )
        eigval, eigvec = jeig.eig(matrix, backend=backend)
        eigval, eigvec = _match_eigs(eigval, eigvec, expected_eigval, expected_eigvec)

        onp.testing.assert_allclose(eigval, expected_eigval, err_msg=(backend, shape))
        onp.testing.assert_allclose(eigvec, expected_eigvec, err_msg=(backend, shape))

    @parameterized.expand(BACKENDS)
    def test_set_backend(self, backend):
        self.assertEqual(_jeig._DEFAULT_BACKEND, jeig.EigBackend.TORCH)
        jeig.set_backend(backend)
        self.assertEqual(_jeig._DEFAULT_BACKEND, backend)
        jeig.set_backend(jeig.EigBackend.TORCH)
        self.assertEqual(_jeig._DEFAULT_BACKEND, jeig.EigBackend.TORCH)

    @parameterized.expand(["lapack", "numpy", "scipy", "torch"])
    def test_set_backend_with_str(self, backend_str):
        self.assertEqual(_jeig._DEFAULT_BACKEND, jeig.EigBackend.TORCH)
        jeig.set_backend(backend_str)
        self.assertEqual(
            _jeig._DEFAULT_BACKEND, jeig.EigBackend.from_string(backend_str)
        )
        jeig.set_backend(jeig.EigBackend.TORCH)
        self.assertEqual(_jeig._DEFAULT_BACKEND, jeig.EigBackend.TORCH)

    @parameterized.expand(BACKENDS)
    def test_no_unwanted_type_promotion(self, backend):
        matrix = jax.random.normal(jax.random.PRNGKey(0), (64, 64), dtype=jnp.float32)

        eigvals, eigvecs = jeig.eig(matrix, backend=backend)
        self.assertEqual(eigvals.dtype, jnp.complex64)
        self.assertEqual(eigvecs.dtype, jnp.complex64)

        eigvals, eigvecs = jeig.eig(matrix.astype(jnp.complex128), backend=backend)
        self.assertEqual(eigvals.dtype, jnp.complex128)
        self.assertEqual(eigvecs.dtype, jnp.complex128)


class ForceX64Test(unittest.TestCase):
    @parameterized.expand(BACKENDS)
    def test_force_x64_real(self, backend):
        matrix = jax.random.normal(
            jax.random.PRNGKey(0), (3, 2, 10, 10), dtype=jnp.float32
        )
        eigvec_force, eigval_force = jeig.eig(matrix, backend, force_x64=True)
        eigvec_x64, eigval_x64 = jeig.eig(
            matrix.astype(jnp.float64), backend, force_x64=False
        )

        self.assertEqual(eigval_force.dtype, jnp.complex64)
        self.assertEqual(eigvec_force.dtype, jnp.complex64)
        self.assertEqual(eigval_x64.dtype, jnp.complex128)
        self.assertEqual(eigvec_x64.dtype, jnp.complex128)

        onp.testing.assert_array_equal(eigvec_force, eigvec_x64.astype(onp.complex64))
        onp.testing.assert_array_equal(eigval_force, eigval_x64.astype(onp.complex64))

    @parameterized.expand(BACKENDS)
    def test_force_x64_complex(self, backend):
        mr, mi = jax.random.normal(
            jax.random.PRNGKey(0), (2, 3, 2, 10, 10), dtype=jnp.float32
        )
        matrix = mr + 1j * mi
        eigvec_force, eigval_force = jeig.eig(matrix, backend, force_x64=True)
        eigvec_x64, eigval_x64 = jeig.eig(
            matrix.astype(jnp.complex128), backend, force_x64=False
        )

        self.assertEqual(eigval_force.dtype, jnp.complex64)
        self.assertEqual(eigvec_force.dtype, jnp.complex64)
        self.assertEqual(eigval_x64.dtype, jnp.complex128)
        self.assertEqual(eigvec_x64.dtype, jnp.complex128)

        onp.testing.assert_array_equal(eigvec_force, eigvec_x64.astype(onp.complex64))
        onp.testing.assert_array_equal(eigval_force, eigval_x64.astype(onp.complex64))
