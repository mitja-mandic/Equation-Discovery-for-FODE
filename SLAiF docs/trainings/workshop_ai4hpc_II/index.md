---
title: BERTopic for Austrian Reddit
subTitle: Modeling Political Discourse Before and After the 2024 EU Elections
language: "en"
tocInHeader: true
chapters:
  - ./01-introduction-to-bertopic
  - ./02-reddit-data-preprocessing
  - ./03-bertopic-implementation
  - ./04-llm-enhancement-and-open-challenges
---

**Author:** Biljana Mileva Boshkoska  
**Email:** biljana.mileva@fis.unm.si  
**Affiliation:** Faculty of Information Studies in Novo mesto (FIS)

This book is a self-contained guide to using **BERTopic** for topic modeling on real-world, non-English social media data. It is built around a single running case study: comments from the r/Austria subreddit, collected before and after the 2024 EU Parliament elections, written in German and Austrian German.

By working through this material, you will learn how to:

- understand the ideas behind BERTopic and why it improves on traditional topic modeling approaches such as LDA,
- preprocess noisy, multilingual social media text for topic modeling,
- train and inspect BERTopic models on German-language data,
- compare discourse across two time periods (pre- and post-election), and
- use large language models (LLMs) to turn raw keyword clusters into human-readable topic labels.

## Dataset

The case study uses comments from the **r/Austria** subreddit, spanning the period around the 2024 EU elections:

- **Pre-election window:** April 1 – June 9, 2024
- **Post-election window:** June 10 – July 31, 2024
- **Language:** German, including Austrian German dialect and code-switched text

<Sidenote>
"Austrian German" here refers to the regional variety of German spoken in Austria, which differs from Standard German in vocabulary, spelling conventions, and some grammar. It is treated by most language tools as German (`de`), which has practical consequences you'll see in [Reddit Data Preprocessing](./02-reddit-data-preprocessing/).
</Sidenote>

## How this book is organized

The book has four chapters, each scoped to a single stage of the workflow:

1. **[Introduction to BERTopic](./01-introduction-to-bertopic/)** — what topic modeling is, how BERTopic's pipeline works, and why it is well suited to multilingual social media text.
2. **[Reddit Data Preprocessing](./02-reddit-data-preprocessing/)** — cleaning, filtering, and splitting raw Reddit exports into a form suitable for modeling.
3. **[BERTopic Implementation](./03-bertopic-implementation/)** — configuring, training, and inspecting BERTopic models on the pre- and post-election datasets.
4. **[LLM Enhancement & Open Challenges](./04-llm-enhancement-and-open-challenges/)** — using LLMs to generate readable topic labels, and a tour of open research problems in neural topic modeling.

Each chapter is meant to be read in order, since later chapters assume the dataset and models built in earlier ones. Together they form a complete pipeline: from a raw CSV export of Reddit comments to interpretable, LLM-labeled topics comparing discourse before and after an election.

## Prerequisites

This book assumes working familiarity with Python and pandas, and a conceptual (not necessarily hands-on) understanding of embeddings and clustering. No prior experience with topic modeling specifically is assumed.
