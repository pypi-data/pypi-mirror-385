# gemm

General Matrix Multiplication (GEMM) operation that computes C = A × B^T. This is a fundamental linear algebra operation used in neural networks for layer computations, attention mechanisms, and other matrix transformations.

Variants:
- FP16 GEMM: Uses 16-bit floating point (FP16) inputs for A and B matrices
- FP8 GEMM: Uses 8-bit floating point (FP8) inputs for A and B matrices, with scaling factors to maintain numerical stability

Axes (3 dimensions):
- `M`: variable
- `N`, `K`: constant

Inputs (2 or 4 tensors):
- `A`: [M, K]
- `B`: [N, K]
- Scaling factors for FP8 GEMM:
    - `A_scale`: [M]
    - `B_scale`: [N]

Outputs (1 tensor):
- `C`: [M, N]
