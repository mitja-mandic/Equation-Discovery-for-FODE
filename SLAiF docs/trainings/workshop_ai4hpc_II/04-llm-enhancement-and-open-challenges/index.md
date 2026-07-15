# LLM Enhancement & Open Challenges

The previous chapter left off with raw c-TF-IDF keyword lists like `fpö, grünen, partei, wählen, österreich, politik` describing each topic. This chapter covers how to turn keyword lists like that into genuinely readable labels using LLMs, and closes with a survey of open problems in this area of research.

## The limits of keyword-based labels

c-TF-IDF keyword lists are useful, but they have real limitations as a way of communicating what a topic is about:

- they're often ambiguous — it isn't always obvious what a keyword list is actually describing,
- they carry no context or narrative,
- they're difficult for non-expert readers to interpret, and
- they simply aren't very human-readable.

Compare the raw keyword list above to a generated label like **"Austrian Political Parties and EU Elections."** The label conveys the same underlying topic far more clearly — this is exactly what LLM-based labeling is for.

## Two approaches to LLM labeling

BERTopic's `representation` module supports plugging an LLM in to generate labels directly from a topic's keywords and representative documents. Two natural options are a local open-weight model and a hosted API model, and they come with different trade-offs.

**Option 1: a local model (e.g. Llama 2).** Running a model locally is free, keeps all data on your own hardware, and has no API rate limits to work around. In exchange, it requires a GPU, runs slower than a hosted API call, and involves more setup complexity.

**Option 2: a hosted API model (e.g. GPT-4o-mini).** A hosted model is fast, generally produces higher-quality labels out of the box, and requires very little setup. The trade-offs are that it costs money per call, sends your data to a third-party provider, and is subject to that provider's rate limits.

For a workshop setting where speed and ease of setup matter more than cost or data locality, a hosted API model such as GPT-4o-mini is the more practical default — though a local model remains the right choice whenever data cannot leave your own infrastructure.

### Using a local model

```python
from bertopic.representation import LlamaCPP

# Define prompt
prompt = """
<s>[INST]
I have a topic with these keywords: [KEYWORDS]

Representative documents:
[DOCUMENTS]

Generate a concise German label (5 words max) for this topic.

Label: [/INST]
"""

# Initialize Llama
llama_model = LlamaCPP(
    model="path/to/llama-2-7b-chat.gguf",
    prompt=prompt,
    n_gpu_layers=-1,
    temperature=0.3,
    max_tokens=50
)

# Use in BERTopic
topic_model = BERTopic(
    embedding_model=embedding_model,
    representation_model=llama_model
)
```

### Using a hosted API model

```python
from bertopic.representation import OpenAI
import openai

# Set API key
openai.api_key = "your-api-key-here"

# Define prompt
prompt = """
I have a topic from Austrian Reddit with these keywords:
[KEYWORDS]

Representative comments:
[DOCUMENTS]

Generate a concise German label (5 words max) that describes
this topic clearly.

Label:
"""

# Initialize OpenAI
openai_model = OpenAI(
    model="gpt-4o-mini",
    prompt=prompt,
    chat=True,
    nr_docs=5,
    delay_in_seconds=1
)
```

### Training with LLM enhancement

```python
# Create BERTopic with GPT-4o-mini
topic_model_llm = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    representation_model=openai_model,
    min_topic_size=15,
    language='german',
    verbose=True
)

# Train
topics, probs = topic_model_llm.fit_transform(documents_pre)

# View LLM-generated labels
topic_info = topic_model_llm.get_topic_info()
print(topic_info[['Topic', 'Count', 'Name', 'Representation']])
```

Because each topic now requires an API round-trip, training with LLM-based representation takes noticeably longer than training with c-TF-IDF alone — typically an extra 1–2 seconds per topic.

## Writing good labeling prompts

A handful of principles make LLM-generated labels noticeably more reliable:

1. **Be clear and specific.** Ask directly for "a label," not an open-ended "what is this about?"
2. **Constrain the output.** A constraint like "5 words max" prevents rambling, multi-sentence outputs that defeat the purpose of a label.
3. **Provide context.** Include both the keyword list and a few representative documents, not keywords alone.
4. **Be language-specific.** For German-language topics, explicitly ask for a German label, rather than leaving the output language to chance.

For example, a vague prompt like *"What is this topic?"* reliably produces worse results than a constrained one like *"Generate a concise German label (5 words max) for this Austrian Reddit topic."*

## Keywords vs. LLM labels, side by side

| Topic | c-TF-IDF Keywords | LLM Label |
|---|---|---|
| 0 | fpö, grünen, partei, wählen, österreich | Österreichische Parteien und EU-Wahlen |
| 1 | ukraine, russland, krieg, nato, putin | Ukraine-Russland Konflikt und NATO |
| 2 | migration, flüchtlinge, asyl, integration | Migration und Asylpolitik in Österreich |
| 3 | österreich, türkei, spiel, favorit, fußball | Österreich vs. Türkei Fußballspiel |
| 4 | dialekt, deutsch, hochdeutsch, sprache | Österreichische Sprache und Dialekte |

The pattern holds across every row: the LLM-generated labels are consistently more interpretable and contextual than the raw keyword lists, at the cost of an extra inference step per topic.

## Open challenges in neural topic modeling

The pipeline in this book — clean data, embed, reduce, cluster, represent, label — is a solid foundation, but it leaves a number of real research problems unresolved. Five are worth knowing about if you plan to take this work further.

### 1. Temporal dynamics

Training separate models for the pre- and post-election periods, as this book does, sidesteps a genuinely hard problem: topics evolve continuously over time, and there is no automatic way to track that evolution or to align topics discovered independently across two periods. A question like *"how did the 'immigration' topic actually change from before the election to after?"* is not something the current pipeline can answer directly — a human has to draw that connection by comparing keyword lists manually. Active research directions here include online or incremental BERTopic variants, automatic topic alignment across time windows, and methods for detecting when a topic splits into two or merges from two into one.

### 2. Multilingual modeling

This case study sidesteps multilingual complexity by filtering down to German-only comments — which means genuinely mixed-language content, like *"Das ist really interesting,"* and comments in other languages entirely, are dropped rather than modeled. Research directions here include true multilingual topic models that don't require choosing a single target language, cross-lingual topic alignment, and better handling of code-switching within a single comment.

### 3. Scalability

Every stage of the pipeline has a real computational cost at scale: embedding generation alone can take 5–10 minutes for 10,000 documents, UMAP is memory-intensive, and HDBSCAN slows down considerably on large datasets. For datasets beyond roughly 100,000 documents, sampling or GPU acceleration become practically necessary rather than optional. Distributed and parallel processing, approximate methods, streaming algorithms, and hierarchical sampling are all active areas of work on this problem.

### 4. Evaluation

There is no settled answer to "how do you measure whether a set of topics is good?" Existing metrics — topic coherence measures like NPMI and C_V, topic diversity, and human evaluation — were largely designed with LDA in mind, don't transfer cleanly to neural topic models, and human evaluation in particular is expensive to scale. There is no consensus on what "good" topics look like in the abstract, since topic quality is inherently task-dependent. New metrics designed specifically for neural topic models, automated quality assessment, and task-based evaluation frameworks are all open directions here.

### 5. Bias and fairness

Topic models can amplify biases present in their inputs at several points: the pre-trained embedding model itself, the demographic skew of the training data (Reddit's user base is not representative of the general population), and even in how a human interprets a resulting topic. In an Austrian Reddit context specifically, this can surface as over-representation of certain political viewpoints, gendered language patterns, or ethnic and cultural biases baked into the underlying discourse. Bias detection methods for topic models, debiasing techniques, fairness-aware algorithms, and clearer ethical guidelines for this kind of analysis are all still developing areas.

<Sidenote>
None of these five challenges are reasons to avoid using BERTopic — they're reasons to report results carefully. A pipeline like the one in this book is a solid starting point for exploratory analysis; treating its output as a definitive, unbiased account of "what Austria was really talking about" would overstate what the method can currently guarantee.
</Sidenote>

## Workshop summary

Across the four chapters of this book:

- **[Introduction to BERTopic](../01-introduction-to-bertopic/)** covered BERTopic's four-step pipeline and its advantages over traditional approaches like LDA.
- **[Reddit Data Preprocessing](../02-reddit-data-preprocessing/)** covered cleaning Austrian Reddit data and handling German-language text specifically.
- **[BERTopic Implementation](../03-bertopic-implementation/)** covered training models and comparing discourse across the pre- and post-election periods.
- This chapter covered LLM-based label enhancement and a tour of open research challenges.

**Key takeaways:**

- BERTopic is a powerful, practical tool for social media analysis.
- Multilingual embedding models handle German and Austrian German reasonably well out of the box.
- Careful preprocessing is not optional — it is what makes or breaks topic quality on noisy, informal text.
- LLMs meaningfully improve the interpretability of topic labels over raw keyword lists.
- Several substantial research problems — temporal dynamics, multilingual modeling, scalability, evaluation, and fairness — remain genuinely open.

**Suggested next steps** if you want to take this further: apply the pipeline to your own datasets, experiment with different parameter choices (particularly `min_topic_size` and the embedding model), try alternative embedding models for your specific language or domain, explore temporal topic analysis directly, and consider contributing to the open-source BERTopic ecosystem.

## Resources

**Documentation:**

- [BERTopic documentation](https://maartengr.github.io/BERTopic/)
- [Sentence-Transformers documentation](https://www.sbert.net/)

**Code:**

- [BERTopic on GitHub](https://github.com/MaartenGr/BERTopic)

**Further reading:**

- Grootendorst, M. (2022). *BERTopic: Neural topic modeling with a class-based TF-IDF procedure.*

---

*This material is adapted from a SLAIF workshop on BERTopic for Austrian Reddit discourse analysis. © 2026 SLAIF, licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). SLAIF (Slovenian AI Factory) is funded by the Ministry of Higher Education, Science and Innovation of the Republic of Slovenia; under a EuroHPC JU call, the project received a positive funding decision under the Horizon Europe and Digital Europe programmes.*
