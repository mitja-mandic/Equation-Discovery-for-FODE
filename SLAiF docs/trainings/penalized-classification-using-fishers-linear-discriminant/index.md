---
title: "Penalized classification using Fisher’s linear discriminant"
subTitle: "A guided reading companion to Witten and Tibshirani (2011)"
language: "en"
tocInHeader: true
chapters:
  - ./01-introduction
  - ./02-fishers-discriminant-problem
  - ./03-a-brief-review-of-minorization-algorithms
  - ./04-the-penalized-lda-proposal
  - ./05-examples
  - ./06-classical-formulations-and-high-dimensional-extensions
  - ./07-connections-with-existing-methods
  - ./08-discussion-and-reading-notes
---

This book is a structured companion to the 2011 paper by Daniela M. Witten and Robert Tibshirani,
“Penalized classification using Fisher’s linear discriminant.”

The paper is a technical one, but the main idea is straightforward: if classical LDA becomes unstable
or hard to interpret in the high-dimensional setting, then the discriminant vectors themselves should
be regularized in a way that keeps the classifier useful and readable.

This companion book follows the paper’s logic, but it rewrites the material as a teaching resource.
The goal is not to reproduce the paper verbatim. The goal is to make the argument easier to read,
easier to remember, and easier to revisit later when you need the method.

## What this book covers

- why standard LDA breaks down when the number of features is large relative to the number of samples
- how Fisher’s discriminant problem is formulated
- why minorization-maximization is useful here
- how penalized LDA is defined and optimized
- how the method behaves in simulations and gene-expression examples
- how it relates to other sparse classification methods

## How to use it

Read the chapters in order the first time. After that, the later chapters work well as a reference
when you need to recall how the proposal differs from optimal scoring, nearest shrunken centroids,
or other sparse LDA variants.

