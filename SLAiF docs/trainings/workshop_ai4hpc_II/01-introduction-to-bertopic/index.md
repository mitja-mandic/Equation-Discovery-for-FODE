# Introduction to BERTopic

## What is topic modeling?

Topic modeling is the task of automatically discovering abstract "topics" that occur across a collection of documents, without needing anyone to label those documents in advance.

Take a collection of 10,000 comments from the r/Austria subreddit. Some of them discuss politics, some discuss immigration, some discuss football, and others discuss Austrian culture. A topic model reads all of them and, on its own, groups the comments into clusters like these — with each comment potentially belonging to one or more topics.

This is useful for several reasons:

- it lets you understand a large text collection quickly, without reading every document,
- it surfaces trends and patterns that would be hard to spot manually,
- it makes it possible to compare discourse across time periods, and
- it can help detect emerging narratives as they form.

That last point is exactly what this book's case study is built around: using topic modeling to compare what Austrian Reddit users were talking about before and after the 2024 EU elections.

## From bag-of-words to context: LDA vs. BERTopic

Traditional topic modeling, most commonly **Latent Dirichlet Allocation (LDA)**, treats text as a "bag of words": it counts word occurrences without regard to context or word order. This makes it fast, but it has a real limitation for multilingual, informal text — it cannot recognize that two different words mean the same thing. To an LDA model, "Österreich" and "Austria" are simply two unrelated tokens.

**BERTopic** takes a different approach. It represents documents using contextual embeddings — dense numerical vectors produced by a neural language model — so that semantically similar text ends up with similar vectors, regardless of the exact words used. To a BERTopic pipeline, "Österreich" and "Austria" are recognized as referring to the same concept, because the model has learned semantic relationships between words rather than just their surface form.

The trade-off is speed: BERTopic requires more compute than LDA, since it involves running a full embedding model over the corpus rather than counting word frequencies. In exchange, it captures meaning that LDA cannot.

## The four-step BERTopic pipeline

BERTopic works as a pipeline of four stages:

```text
Documents → Embed → Reduce → Cluster → Represent
```

1. **Embed** — Convert each document into a numerical vector using a Sentence-Transformers model. These embeddings capture semantic meaning, so that similar texts end up with similar vectors.
2. **Reduce** — Apply dimensionality reduction, typically with UMAP, to bring embeddings from hundreds of dimensions down to a handful (commonly 5–10) while preserving the structure of the data.
3. **Cluster** — Group the reduced vectors using HDBSCAN, which automatically determines the number of clusters and can flag documents that don't belong to any clear group.
4. **Represent** — Extract characteristic keywords for each resulting cluster using class-based TF-IDF (c-TF-IDF), producing an interpretable label for each topic.

The next four sections walk through each of these steps in turn.

### Step 1: Embedding documents

The goal of this step is to convert raw text into numerical vectors that capture meaning. BERTopic does this with **Sentence-Transformers**, a family of pre-trained BERT-based models optimized for semantic similarity, several of which are multilingual.

For this case study's Austrian German text, the workshop uses `paraphrase-multilingual-MiniLM-L12-v2`, a model trained across many languages that handles German, Austrian German, and its dialectal variants, producing 384-dimensional vectors. As an example, a sentence like *"Österreich war Favorit"* is mapped to a 384-number vector — something like `[0.23, -0.45, 0.67, ...]`.

<Sidenote>
The specific choice of embedding model matters more for multilingual or dialectal text than it does for standard, well-resourced languages. A model that has not seen much German — let alone Austrian German — will produce noisier embeddings, which in turn produces noisier topics downstream.
</Sidenote>

### Step 2: Dimensionality reduction with UMAP

384 dimensions is far too many for clustering algorithms to work with efficiently or reliably — this is sometimes called the "curse of dimensionality." **UMAP** (Uniform Manifold Approximation and Projection) addresses this by reducing the embeddings down to around 5–10 dimensions while preserving both the local and global structure of the data. Compared to alternatives like t-SNE, UMAP is substantially faster, which matters when working with tens of thousands of documents.

### Step 3: Clustering with HDBSCAN

Once the embeddings are reduced, **HDBSCAN** groups similar documents into topics. It has several properties that make it a good fit for this task:

- it does not require specifying the number of topics up front,
- it can find clusters of varying density, rather than assuming all clusters are similarly shaped,
- it has a hierarchical structure, and
- it explicitly identifies outliers rather than forcing every document into a cluster.

That last point deserves elaboration. Not every comment fits a clear topic — very short comments ("lol", "agreed"), off-topic tangents, and genuinely unique perspectives all exist in real data. HDBSCAN assigns these to a special outlier group (labeled `-1`) rather than distorting a real topic to accommodate them. For interpretability, it is generally better to identify these outliers explicitly than to force them into a topic they don't belong to.

### Step 4: Representing topics with c-TF-IDF

The final step describes each topic with a set of characteristic keywords, using **class-based TF-IDF (c-TF-IDF)**. The idea is a variation on ordinary TF-IDF applied at the topic level rather than the document level:

1. treat every document in a topic as one combined "document,"
2. calculate term frequency within that combined topic-document,
3. calculate inverse frequency across all topics, and
4. keywords with high scores are the ones that are frequent within a topic but rare elsewhere.

For example, an "Austrian Politics" topic in this dataset might be represented by the keywords `fpö, grünen, partei, wählen, österreich, politik` — terms that show up often within that topic's comments but rarely in comments belonging to other topics.

## Why BERTopic fits this case study

Putting the pipeline together, BERTopic has five properties that make it a strong choice for analyzing Austrian Reddit discourse:

1. **Semantic understanding** — it recognizes that "Österreich" and "Austria" refer to the same thing, and handles synonyms and context generally.
2. **Multilingual support** — it works across German and Austrian German, and tolerates code-switching between languages.
3. **Automatic topic discovery** — the number of topics does not need to be specified in advance; the model adapts to the data.
4. **Outlier detection** — noisy or off-topic comments are identified rather than forced into a topic.
5. **Rich visualizations** — BERTopic ships with interactive plotting tools that make topics easy to explore and interpret.

## The case study: Austrian Reddit before and after the 2024 EU elections

The research question driving this book's case study is: **how did political discourse on r/Austria change around the 2024 EU elections?**

The dataset spans:

- **Source:** the r/Austria subreddit
- **Language:** German / Austrian German
- **Pre-election window:** April 1 – June 9, 2024
- **Post-election window:** June 10 – July 31, 2024

Based on the subject matter typically discussed on r/Austria around this period, the topics we expect to emerge include Austrian politics (particularly the FPÖ and the Greens), immigration and integration, the Ukraine–Russia conflict, Austrian culture and language, and — since it coincided with Euro 2024 — football.

The next chapter covers how the raw Reddit export is cleaned and prepared before any of this modeling can happen.

