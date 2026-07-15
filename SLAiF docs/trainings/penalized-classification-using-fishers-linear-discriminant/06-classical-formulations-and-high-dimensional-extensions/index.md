# Classical formulations and high-dimensional extensions

This chapter is the bridge between the paper’s proposal and the older LDA literature.

The authors revisit three equivalent classical views of LDA:

- the normal-model formulation
- the optimal scoring formulation
- Fisher’s discriminant formulation

They then explain how these viewpoints behave once the feature dimension becomes large.

The main lesson is that not every LDA formulation breaks in the same way, and not every extension is
trying to fix the same problem. Some approaches focus on the covariance estimate, some on the scoring
formulation, and some on sparsity directly.

## Why this chapter exists

It is easy to think of all high-dimensional LDA methods as variants of one another. The paper shows that
they are related, but not identical, and that the choice of formulation affects both the objective and
the interpretation.

