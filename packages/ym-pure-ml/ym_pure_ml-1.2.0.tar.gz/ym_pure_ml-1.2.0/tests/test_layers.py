# layers
import unittest as ut
import numpy as np

# Public API
from pureml.machinery import Tensor
from pureml.layers import Affine, Dropout, BatchNorm1d, Embedding
from pureml.general_math import mean

def _rng(seed=0):
    return np.random.default_rng(seed)


# --------------------------- Affine ---------------------------
class TestAffine(ut.TestCase):
    def test_forward_shapes_batch_and_single(self):
        B, n, m = 7, 5, 3
        layer = Affine(n, m)
        Xb = Tensor(_rng(0).standard_normal((B, n)))
        Yb = layer(Xb)
        self.assertEqual(Yb.data.shape, (B, m))

        # Single example (1D); layer should accept and return 1D output
        x = Tensor(_rng(1).standard_normal(n))
        y = layer(x)
        self.assertEqual(y.data.shape, (m,))

    def test_backward_grads_match_formulas(self):
        B, n, m = 8, 4, 6
        rng = _rng(2)
        layer = Affine(n, m)
        X = Tensor(rng.standard_normal((B, n)), requires_grad=True)
        Y = layer(X)                     # (B,m)

        # Backward with upstream ones to keep formulas simple
        U = np.ones_like(Y.data)
        Y.backward(U)

        # Expected grads:
        W = layer.W.data                 # (n,m)
        dX_expected = U @ W.T            # (B,n)
        dW_expected = X.data.T @ U       # (n,m)
        db_expected = U.sum(axis=0)      # (m,)

        np.testing.assert_allclose(X.grad, dX_expected, rtol=1e-6, atol=1e-8)
        self.assertIsNotNone(layer.W.grad)
        self.assertIsNotNone(layer.b.grad)
        np.testing.assert_allclose(layer.W.grad, dW_expected, rtol=1e-6, atol=1e-8)
        np.testing.assert_allclose(layer.b.grad, db_expected, rtol=1e-6, atol=1e-8)

    def test_bias_broadcasting(self):
        B, n, m = 5, 3, 4
        layer = Affine(n, m)
        X = Tensor(np.ones((B, n)), requires_grad=True)
        Y = layer(X)
        Y.backward(np.ones_like(Y.data))
        # db should be all B's (sum of ones over batch)
        np.testing.assert_allclose(layer.b.grad, np.full((m,), B, dtype=float), rtol=1e-6, atol=1e-8)


# --------------------------- Dropout ---------------------------
class TestDropout(ut.TestCase):
    def test_eval_identity(self):
        X = Tensor(_rng(0).standard_normal((4, 6)))
        d = Dropout(p=0.75, seed=123).eval()  # eval => identity
        Y = d(X)
        np.testing.assert_allclose(Y.data, X.data, rtol=0, atol=0)

    def test_train_p0_identity(self):
        X = Tensor(_rng(1).standard_normal((5, 7)))
        d = Dropout(p=0.0, seed=42).train()   # no drop
        Y = d(X)
        np.testing.assert_allclose(Y.data, X.data, rtol=0, atol=0)

    def test_seeded_determinism(self):
        X = Tensor(np.ones((100, 50)))  # large enough to exercise mask
        d1 = Dropout(p=0.6, seed=2024).train()
        d2 = Dropout(p=0.6, seed=2024).train()
        Y1 = d1(X)
        Y2 = d2(X)
        np.testing.assert_allclose(Y1.data, Y2.data, rtol=0, atol=0)


# --------------------------- BatchNorm1d ---------------------------
class TestBatchNorm1d(ut.TestCase):
    def test_running_stats_update_in_train(self):
        B, F = 16, 5
        rng = _rng(10)
        bn = BatchNorm1d(F, momentum=0.2).train()

        # Capture initial stats if present; otherwise create placeholders
        rm0 = getattr(bn, "running_mean", None)
        rv0 = getattr(bn, "running_variance", None)
        if rm0 is not None: rm0 = rm0.data.copy()
        if rv0 is not None: rv0 = rv0.data.copy()

        X = Tensor(rng.standard_normal((B, F)))
        _ = bn(X)   # one training forward should nudge running stats

        # Running stats should be finite and (likely) changed
        self.assertTrue(hasattr(bn, "running_mean"))
        self.assertTrue(hasattr(bn, "running_variance"))
        self.assertTrue(np.all(np.isfinite(bn.running_mean.data)))
        self.assertTrue(np.all(np.isfinite(bn.running_variance.data)))
        if rm0 is not None:
            self.assertFalse(np.allclose(bn.running_mean.data, rm0))
        if rv0 is not None:
            self.assertFalse(np.allclose(bn.running_variance.data, rv0))

    def test_eval_does_not_mutate_running_stats(self):
        B, F = 8, 3
        rng = _rng(11)
        bn = BatchNorm1d(F, momentum=0.1).train()
        _ = bn(Tensor(rng.standard_normal((B, F))))  # prime running stats

        rm_before = bn.running_mean.data.copy()
        rv_before = bn.running_variance.data.copy()

        bn.eval()
        _ = bn(Tensor(rng.standard_normal((B, F))))  # eval forward; should not change stats

        np.testing.assert_allclose(bn.running_mean.data, rm_before, rtol=0, atol=0)
        np.testing.assert_allclose(bn.running_variance.data, rv_before, rtol=0, atol=0)

    def test_backward_input_grad_shape(self):
        B, F = 10, 4
        rng = _rng(12)
        bn = BatchNorm1d(F, momentum=0.2).train()
        X = Tensor(rng.standard_normal((B, F)), requires_grad=True)
        Y = bn(X)
        L = mean((Y * Y))
        L.backward()
        # Must produce input gradients of same shape
        self.assertIsNotNone(X.grad)
        self.assertEqual(X.grad.shape, X.data.shape)


# --------------------------- Embedding ---------------------------
class TestEmbedding(ut.TestCase):
    def test_forward_shapes_and_values(self):
        V, D = 6, 4
        # deterministic weights to compare against numpy gather
        W_arr = np.arange(V * D, dtype=np.float64).reshape(V, D)
        W = Tensor(W_arr, requires_grad=True)
        emb = Embedding(V, D, W=W)

        idx_np = np.array([[1, 3, 2],
                           [0, 4, 5]], dtype=np.int64)
        idx = Tensor(idx_np, requires_grad=False)

        Y = emb(idx)
        self.assertEqual(Y.data.shape, (2, 3, D))
        np.testing.assert_allclose(Y.data, W_arr[idx_np], rtol=0, atol=0)

    def test_backward_accumulates_repeats_and_respects_padding(self):
        V, D = 7, 3
        pad_idx = 0
        W = Tensor(np.zeros((V, D), dtype=np.float64), requires_grad=True)
        emb = Embedding(V, D, pad_idx=pad_idx, W=W)

        idx_np = np.array([[1, 1, 3, 1, 0],
                        [2, 0, 2, 2, 0]], dtype=np.int64)
        idx = Tensor(idx_np, requires_grad=False)

        Y = emb(idx)
        Y.backward(np.ones_like(Y.data))

        counts = np.bincount(idx_np.reshape(-1), minlength=V)
        expected = np.repeat(counts[:, None], D, axis=1).astype(np.float64)
        expected[pad_idx, :] = 0.0

        np.testing.assert_allclose(emb.W.grad, expected, rtol=1e-6, atol=1e-8)
        np.testing.assert_allclose(emb.W.data[pad_idx], np.zeros(D), rtol=0, atol=0)

    def test_backward_matches_manual_scatter_add_with_random_upstream(self):
        V, D = 5, 2
        W = Tensor(np.zeros((V, D), dtype=np.float64), requires_grad=True)
        emb = Embedding(V, D, W=W)

        idx_np = np.array([[4, 1, 1],
                           [3, 4, 0]], dtype=np.int64)
        idx = Tensor(idx_np, requires_grad=False)
        Y = emb(idx)

        rng = _rng(123)
        upstream = rng.standard_normal(Y.data.shape)
        Y.backward(upstream)

        # manual scatter-add
        I = idx_np.reshape(-1)
        G = upstream.reshape(-1, D)
        dW_manual = np.zeros((V, D), dtype=np.float64)
        for i, g in zip(I, G):
            dW_manual[i] += g

        np.testing.assert_allclose(emb.W.grad, dW_manual, rtol=1e-6, atol=1e-8)

    def test_out_of_range_indices_raise(self):
        V, D = 4, 3
        emb = Embedding(V, D)
        idx = Tensor(np.array([[0, 1, 4]], dtype=np.int64), requires_grad=False)  # 4 is OOR
        with self.assertRaises(IndexError):
            _ = emb(idx)

    def test_float_indices_are_cast_to_int(self):
        V, D = 6, 3
        W_arr = np.arange(V * D, dtype=np.float64).reshape(V, D)
        W = Tensor(W_arr, requires_grad=True)
        emb = Embedding(V, D, W=W)

        idx_int = np.array([[1, 2],
                            [3, 0]], dtype=np.int64)
        idx_float = idx_int.astype(np.float64)

        Y1 = emb(Tensor(idx_int, requires_grad=False))
        Y2 = emb(Tensor(idx_float, requires_grad=False))
        np.testing.assert_allclose(Y1.data, Y2.data, rtol=0, atol=0)

    def test_buffers_roundtrip_padding_idx(self):
        V, D = 5, 4
        emb = Embedding(V, D, pad_idx=2)
        bufs = emb.named_buffers()
        self.assertIn("padding_idx", bufs)
        self.assertEqual(int(bufs["padding_idx"].item()), 2)
        # restore to a different padding index
        emb.apply_state(buffers={"padding_idx": np.asarray(3, dtype=np.int64)})
        self.assertEqual(emb.padding_idx, 3)

    def test_preinitialized_W_shape_validation(self):
        V, D = 4, 3
        badW = Tensor(np.zeros((D, V), dtype=np.float64), requires_grad=True)
        with self.assertRaises(ValueError):
            _ = Embedding(V, D, W=badW)


if __name__ == "__main__":
    ut.main(verbosity=2)
