# Introduction

Witten and Tibshirani’s paper starts from a practical complaint: classical linear discriminant analysis
works well in the low-dimensional regime, but it becomes awkward when the number of features is large
relative to the number of observations.

There are two separate problems in that setting.

- The within-class covariance estimate can become singular or nearly singular, which makes the standard
  LDA rule unstable or undefined.
- Even when the classifier can still be computed, it is often hard to interpret because it uses all
  features at once.

The paper’s answer is to regularize the discriminant vectors directly. That keeps the classification
problem tied to Fisher’s geometry, while adding a form of sparsity or smoothness that is easier to
understand in high dimensions.

## The main claim

The authors argue that a penalized version of Fisher’s discriminant problem is a natural route to
high-dimensional classification. The method is designed to preserve the structure of LDA, but to make
the discriminant vectors sparse or structured enough to be interpretable.

## Why this matters

This is not just a feature-selection trick. The point is to keep the classification rule close to the
classical Fisher framework while solving the stability and interpretability problems that appear when
data are wide rather than tall.

