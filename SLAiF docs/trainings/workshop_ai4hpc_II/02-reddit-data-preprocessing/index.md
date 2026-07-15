# Reddit Data Preprocessing

Before any modeling can happen, the raw Reddit export needs to be cleaned. This chapter walks through the full preprocessing pipeline used for the Austrian Reddit dataset, from loading the raw CSV to producing separate pre- and post-election files ready for BERTopic.

## Understanding the dataset

Each row in the raw export represents a single comment, with the following fields:

- **Comment ID**
- **Author**
- **Comment** (the text itself)
- **Timestamp**

A representative row looks like this:

```text
l49yp8h, Fabiennethefemboy, "Des schnizl mit zimt", 2024-05-16 07:40:47
```

Real-world Reddit exports come with a predictable set of problems: duplicate comments, very short comments that carry little topical signal, deleted or removed content, Austrian German dialect that standard NLP tools handle inconsistently, and comments that mix languages mid-sentence. The preprocessing pipeline below addresses each of these in turn.

## Loading the data

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('austrian_reddit_comments.csv')

print(f"Total comments: {len(df)}")
print(f"Date range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")

# Display first few rows
print(df.head())

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())
```

## Pipeline overview

The full preprocessing pipeline has six stages:

1. **Remove duplicates** — the same comment can appear more than once.
2. **Filter deleted or removed content** — comments marked `[deleted]` or `[removed]`.
3. **Length filtering** — drop comments that are too short to carry topical signal (under 20 characters).
4. **Clean text** — strip URLs, Reddit-specific markdown, and normalize whitespace.
5. **Language detection** — keep only German-language comments.
6. **Split pre/post election** — using June 9, 2024 as the cutoff date.

### Step 1: Remove duplicates

```python
# Remove exact duplicate comments
before_dedup = len(df)
df = df.drop_duplicates(subset=['Comment'], keep='first')

print(f"Before removing duplicates: {before_dedup}")
print(f"After removing duplicates: {len(df)}")
print(f"Removed: {before_dedup - len(df)} duplicates")
```

Duplicates are common in Reddit exports for a few reasons: the Reddit API can return the same comment more than once across paginated requests, comments get cross-posted, and general data-collection artifacts creep in. It is not unusual for a raw export to contain 50% duplicate rows — a dataset of 25,000 raw comments dropping to around 12,500 unique ones after this step is a realistic outcome.

### Step 2: Filter deleted or removed content

```python
import re

def is_deleted_or_removed(text):
    """Check if comment is deleted or removed."""
    if not isinstance(text, str):
        return True

    text = text.strip().lower()

    # Check for deletion markers
    if text in ['[deleted]', '[removed]', 'deleted', 'removed']:
        return True

    return False

# Filter out deleted/removed comments
df = df[~df['Comment'].apply(is_deleted_or_removed)]

print(f"Remaining comments: {len(df)}")
```

### Step 3: Length filtering

Very short comments — "lol", "agreed," single emoji reactions — rarely carry enough content for topic modeling to work with, and extremely long comments can be low-quality copy-pasted text. Both ends are worth trimming:

```python
# Calculate comment lengths
df['comment_length'] = df['Comment'].str.len()

# Visualize distribution
import matplotlib.pyplot as plt

plt.hist(df['comment_length'], bins=50)
plt.xlabel('Comment Length (characters)')
plt.ylabel('Frequency')
plt.title('Distribution of Comment Lengths')
plt.show()

# Filter by length
min_length = 20    # At least 20 characters
max_length = 5000  # At most 5000 characters

df = df[(df['comment_length'] >= min_length) &
        (df['comment_length'] <= max_length)]

print(f"After length filtering: {len(df)}")
```

<Sidenote>
A histogram of comment lengths is a quick, cheap sanity check: if it shows an unexpected spike at very low or very high lengths, that's usually a sign of bot activity, spam, or a scraping artifact rather than genuine variation in how people write.
</Sidenote>

### Step 4: Clean text

```python
import re

def clean_text(text):
    """Clean Reddit comment text."""
    if not isinstance(text, str):
        return ""

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', ' ', text)

    # Remove Reddit markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove user mentions (u/username)
    text = re.sub(r'/?u/\w+', ' ', text)

    # Remove subreddit mentions (r/subreddit)
    text = re.sub(r'/?r/\w+', ' ', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Apply cleaning
df['cleaned_comment'] = df['Comment'].apply(clean_text)
```

### Step 5: Language detection

```python
from langdetect import detect, LangDetectException

def is_german(text):
    """Detect if text is in German."""
    if len(text) < 30:
        return True  # Too short for reliable detection

    try:
        lang = detect(text)
        return lang == 'de'
    except LangDetectException:
        return True  # Keep if detection fails

# Filter for German comments
df['is_german'] = df['cleaned_comment'].apply(is_german)
df = df[df['is_german']]

print(f"German comments: {len(df)}")
```

Austrian German is detected by standard language-ID tools as plain German (`de`) — there is no separate language code for it. This is convenient here, since it means the filter above keeps Austrian German text without extra handling, but it is worth being aware of: any dialectal or regional variation gets folded into a single "German" bucket rather than being distinguished.

### Step 6: Split pre/post election

```python
# Convert timestamp to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Define election date
election_date = pd.to_datetime('2024-06-09')

# Split dataset
df_pre = df[df['Timestamp'] < election_date]
df_post = df[df['Timestamp'] >= election_date]

print(f"Pre-election comments: {len(df_pre)}")
print(f"Post-election comments: {len(df_post)}")

# Save cleaned datasets
df_pre.to_csv('austrian_reddit_pre_election.csv', index=False)
df_post.to_csv('austrian_reddit_post_election.csv', index=False)
```

## Summary and expected results

The complete pipeline runs in this order: load data, remove duplicates, filter deleted/removed content, apply length filters, clean text, detect language, and split into pre/post-election files.

A realistic outcome for a raw export of around 25,000 comments is a retention rate of roughly 32–40% after every stage — landing at somewhere between 8,000 and 10,000 usable comments split across the two time windows.

<Sidenote>
However automated your pipeline is, always inspect a sample of the cleaned output by hand before moving on to modeling. Automated filters can silently misfire — for instance, over-aggressive URL stripping can mangle otherwise valid comments — and this is much easier to catch by reading twenty rows than by trusting the summary statistics alone.
</Sidenote>

With `austrian_reddit_pre_election.csv` and `austrian_reddit_post_election.csv` in hand, the next chapter covers configuring and training BERTopic on this cleaned data.
