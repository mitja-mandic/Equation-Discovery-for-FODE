# The penalized LDA proposal

This is the central contribution of the paper.

The authors reformulate Fisher’s discriminant problem so that the discriminant vectors can be penalized
directly. The penalty is applied in a way that encourages interpretability, while keeping the method
anchored in the Fisher/LDA viewpoint.

Two concrete versions are emphasized.

- `L1` penalization, which encourages sparse discriminant vectors.
- Fused lasso penalization, which encourages both sparsity and local smoothness when the features have
  an order or adjacency structure.

The paper also shows how the optimization step can be written in a way that is compatible with the
minorization machinery from the previous chapter.

## Why this is the important chapter

This is where the paper stops being a critique of classical LDA and becomes a constructive method.
The proposal is not “replace LDA with some other classifier.” The proposal is “keep Fisher’s objective,
but penalize the discriminant vectors so the result is usable in high dimensions.”

## The conceptual move

The method can also be viewed as a biconvex reformulation of Fisher’s discriminant problem. That is the
bridge between the statistical idea and the iterative algorithm.

