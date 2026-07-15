# Fisher’s discriminant problem

This chapter is the mathematical core of classical LDA.

Fisher’s discriminant problem asks for a low-dimensional projection that separates classes by maximizing
between-class variation relative to within-class variation. In the ordinary full-rank setting, this can
be written as an eigenproblem, which is why the method is so familiar and so computationally convenient.

The paper then shows why this neat picture breaks in high dimensions.

- The within-class covariance matrix becomes singular when the feature space is too large.
- A singular within-class matrix makes the standard objective degenerate.
- A large number of features also makes the resulting direction hard to interpret.

The chapter also surveys earlier attempts to deal with this failure mode, including diagonal or otherwise
positive-definite covariance estimates and related sparse formulations.

## Takeaway

The key point is that the difficulty is not only computational. It is also statistical and interpretive.
The method needs both stability and structure, not just a workaround for singularity.

