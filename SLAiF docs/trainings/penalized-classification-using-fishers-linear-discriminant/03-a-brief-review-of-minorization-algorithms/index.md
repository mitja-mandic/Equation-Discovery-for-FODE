# A brief review of minorization algorithms

The penalized Fisher objective is nonconvex, so the paper does not try to solve it directly with a single
closed-form update.

Instead, it uses a minorization-maximization strategy. The idea is to replace the hard objective with a
sequence of simpler surrogate problems that are easier to optimize and that still move toward a useful
solution.

This matters because the paper’s penalized formulation stays close to Fisher’s discriminant problem, but
the penalty makes the optimization landscape more complicated. Minorization gives a controlled iterative
route through that landscape.

## What to remember

- The algorithm is iterative.
- Each step solves a simpler problem than the original one.
- The approach is general enough to handle convex penalties on the discriminant vectors.

For a reader, the main lesson is that the paper’s contribution is not only a new objective. It is also a
practical way to optimize that objective.

