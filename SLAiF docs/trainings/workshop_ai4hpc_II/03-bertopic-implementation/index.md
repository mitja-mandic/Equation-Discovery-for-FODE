# BERTopic Implementation

With cleaned pre- and post-election datasets in hand, this chapter covers configuring, training, and inspecting BERTopic models on the Austrian Reddit data.

## Installation

```bash
# Install BERTopic with all dependencies
pip install bertopic[all]

# Install multilingual sentence transformers
pip install sentence-transformers

# Install visualization tools
pip install plotly
```

This installs several components that work together:

- `bertopic` — the main library, orchestrating the pipeline described in [Introduction to BERTopic](../01-introduction-to-bertopic/)
- `sentence-transformers` — for generating embeddings
- `umap-learn` — for dimensionality reduction
- `hdbscan` — for clustering
- `plotly` — for the interactive visualizations used later in this chapter

## Loading the preprocessed data

```python
import pandas as pd

# Load pre-election data
df_pre = pd.read_csv('austrian_reddit_pre_election.csv')

# Extract documents
documents_pre = df_pre['cleaned_comment'].tolist()

print(f"Pre-election documents: {len(documents_pre)}")

# Display sample
print("\nSample comments:")
for i, doc in enumerate(documents_pre[:3], 1):
    print(f"{i}. {doc[:100]}...")
```

## Initializing the embedding model

```python
from sentence_transformers import SentenceTransformer

# Use multilingual model for German/Austrian German
embedding_model = SentenceTransformer(
    'paraphrase-multilingual-MiniLM-L12-v2'
)

# Test embedding
sample_text = "Osterreich war Favorit gegen die Turkei"
sample_embedding = embedding_model.encode([sample_text])

print(f"Embedding shape: {sample_embedding.shape}")
# Output: (1, 384) - one document, 384 dimensions
```

This model was chosen for three reasons: it is trained across more than 50 languages, including German; it handles Austrian German variants reasonably well; and it strikes a good balance between speed and embedding quality for a workshop-scale dataset.

## Configuring the vectorizer

The vectorizer determines which words are eligible to appear in a topic's keyword representation. For German text, this means supplying German stop words alongside Reddit-specific noise terms:

```python
from sklearn.feature_extraction.text import CountVectorizer

# German stop words
german_stops = [
    'der', 'die', 'das', 'und', 'ist', 'in', 'zu', 'den',
    'von', 'mit', 'auf', 'fur', 'nicht', 'ein', 'eine',
    'auch', 'sich', 'an', 'werden', 'aus', 'er', 'hat'
]

# Reddit-specific stop words
reddit_stops = [
    'edit', 'deleted', 'removed', 'reddit', 'post',
    'comment', 'thread'
]

all_stops = german_stops + reddit_stops

# Create vectorizer
vectorizer_model = CountVectorizer(
    stop_words=all_stops,
    min_df=2,               # Word must appear in at least 2 documents
    ngram_range=(1, 2)      # Unigrams and bigrams
)
```

## Initializing the BERTopic model

```python
from bertopic import BERTopic

# Create BERTopic model
topic_model_pre = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    min_topic_size=15,   # Minimum 15 documents per topic
    nr_topics='auto',    # Automatic topic number
    language='german',   # For stop words
    verbose=True         # Show progress
)

print("BERTopic model initialized for pre-election data")
```

Three parameters are worth calling out specifically:

- `min_topic_size=15` — topics smaller than this are merged into larger ones or marked as outliers, which keeps the final topic list from being dominated by tiny, noisy clusters.
- `nr_topics='auto'` — the model decides the optimal number of topics itself, rather than requiring you to specify a fixed count in advance.
- `language='german'` — enables German-specific text processing defaults.

## Training the model

```python
# Fit and transform
topics_pre, probabilities_pre = topic_model_pre.fit_transform(
    documents_pre
)

print("\n=== Pre-Election Model Training Complete ===")
print(f"Total documents: {len(documents_pre)}")
print(f"Unique topics: {len(set(topics_pre)) - 1}")  # -1 for outliers

# Check outlier percentage
outliers = (topics_pre == -1).sum()
print(f"Outliers: {outliers} ({outliers/len(topics_pre)*100:.1f}%)")

# Get topic information
topic_info_pre = topic_model_pre.get_topic_info()
print("\n=== Topic Summary ===")
print(topic_info_pre.head(10))
```

Training time is typically 5–15 minutes for a workshop-scale dataset, depending on its size and available hardware.

## Inspecting topics

Once trained, you can inspect any individual topic's keywords and its most representative documents:

```python
# Get keywords for specific topics
print("\n=== Topic 0: Keywords ===")
keywords_0 = topic_model_pre.get_topic(0)
for word, score in keywords_0[:10]:
    print(f"{word}: {score:.4f}")

# Get representative documents
print("\n=== Topic 0: Representative Documents ===")
rep_docs_0 = topic_model_pre.get_representative_docs(0)
for i, doc in enumerate(rep_docs_0[:3], 1):
    print(f"\n{i}. {doc[:200]}...")
```

For this dataset, Topic 0 typically surfaces as the keyword set `fpö, grünen, partei, wählen, österreich` — which a human reader would naturally label **"Austrian Politics and Elections."** Turning raw keyword lists like this into readable labels automatically is the subject of the [next chapter](../04-llm-enhancement-and-open-challenges/).

## Training the post-election model

The pre- and post-election periods are modeled separately, so that each period's topic structure is discovered independently rather than forced to match the other:

```python
# Load post-election data
df_post = pd.read_csv('austrian_reddit_post_election.csv')
documents_post = df_post['cleaned_comment'].tolist()

# Create new model for post-election
topic_model_post = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    min_topic_size=15,
    nr_topics='auto',
    language='german',
    verbose=True
)

# Train
topics_post, probabilities_post = topic_model_post.fit_transform(
    documents_post
)

print(f"\nPost-election topics: {len(set(topics_post)) - 1}")

# Save both models
topic_model_pre.save("bertopic_pre_election")
topic_model_post.save("bertopic_post_election")
```

## Visualizing topics

BERTopic includes built-in, interactive Plotly visualizations that are especially useful for exploring a topic landscape without reading raw keyword lists.

<Sidenote>
This chapter's original workshop materials referenced two Plotly figures at this point — an intertopic distance map and a topic keyword bar chart — that were not carried over into this text edition. Both can be regenerated directly from a trained model with `topic_model.visualize_topics()` and `topic_model.visualize_barchart()`, respectively; what each shows is described below.
</Sidenote>

**Intertopic distance map** (`topic_model.visualize_topics()`) plots every topic as a circle in 2D space, where circle size reflects the number of documents in that topic and distance between circles reflects semantic similarity. Hovering over a circle reveals its keywords. This view is useful for exploring the overall topic landscape, spotting closely related topics that might warrant merging, and — for this case study specifically — comparing the shape of the pre- and post-election topic spaces side by side.

**Topic keyword bar chart** (`topic_model.visualize_barchart()`) shows the c-TF-IDF scores for each topic's top keywords, making it easy to see at a glance which terms are driving a topic's identity. For the pre-election period, example topics include:

- **Topic 0:** `fpö, grünen, partei, wählen`
- **Topic 1:** `ukraine, russland, krieg, nato`
- **Topic 2:** `migration, flüchtlinge, asyl`

## Comparing pre- and post-election topics

```python
# Get topic info for both periods
topics_pre_info = topic_model_pre.get_topic_info()
topics_post_info = topic_model_post.get_topic_info()

print("=== Pre-Election Top 5 Topics ===")
for idx, row in topics_pre_info.head(5).iterrows():
    print(f"Topic {row['Topic']}: {row['Name']}")
    print(f"  Count: {row['Count']}")
    print()

print("\n=== Post-Election Top 5 Topics ===")
for idx, row in topics_post_info.head(5).iterrows():
    print(f"Topic {row['Topic']}: {row['Name']}")
    print(f"  Count: {row['Count']}")
    print()
```

## Expected findings

**Pre-election (April 1 – June 9, 2024):**

1. **Austrian politics & elections** — keywords `fpö, grünen, partei, wählen`; focused on EU election campaigning.
2. **Immigration & integration** — keywords `migration, flüchtlinge, asyl`; heated pre-election debate.
3. **Ukraine–Russia conflict** — keywords `ukraine, russland, krieg, nato`; ongoing geopolitical discussion.
4. **Austrian culture & language** — keywords `österreich, deutsch, dialekt`; identity-focused discussion.

**Post-election (June 10 – July 31, 2024):**

1. **Football (Euro 2024)** — keywords `österreich, türkei, spiel, favorit`; the Austria vs. Turkey match dominated discourse in this window.
2. **Election results & analysis** — keywords `fpö, ergebnis, wahl`; post-election reflection.
3. **Immigration (continued)** — keywords `migration, integration`; ongoing debate, carried over from the pre-election period.
4. **Austrian identity** — keywords `österreich, kultur, hochmut`; national-pride discussion.

The clearest shift between the two periods is the emergence of football as a dominant topic post-election — driven by Euro 2024 coinciding with the post-election window — alongside a shift in the politics topic from campaign framing to results and analysis. Immigration persists across both periods, suggesting it was a stable rather than election-driven topic of discussion.

The next chapter looks at how to turn keyword lists like `fpö, grünen, partei, wählen, österreich` into a properly readable label such as "Austrian Political Parties and EU Elections" — and surveys some of the open problems that remain in this space.
