# Examples

The paper evaluates the proposal in three settings:

- a simulation study
- gene-expression classification data
- timing comparisons against related methods

The simulation work is there to test whether the penalized methods keep their classification quality
while producing more interpretable discriminant vectors.

The gene-expression examples are the more realistic stress test. In that setting, the data are high-
dimensional and noisy, which is exactly where classical LDA tends to struggle.

## What the examples are meant to show

The examples are not just benchmark tables. They are there to demonstrate a tradeoff:

- classical LDA is simple, but it can be unstable and dense
- the penalized versions aim for similar classification behavior with much clearer structure

The timing results are also part of the argument. A method is not very useful if the optimization cost
is unreasonable, so the paper checks that the iterative approach is still practical.

