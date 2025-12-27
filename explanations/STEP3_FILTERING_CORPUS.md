# Step 3: Filtering the Corpus

This document explains how to use the `SpeechCorpus` class located in `src/filtering_corpus/speech_corpus.py` to select subsets of the Trump speech database for specific analyses.

## Overview

The `SpeechCorpus` class is designed to load the speech and transcription data (from Parquet files) and provide an intuitive interface for filtering speeches based on metadata such as date, campaign cycle, location, and speech type (rally vs. non-rally).

## 1. Loading the Corpus

To start, you need to import the class and initialize it. By default, it looks for data in the `data` directory and expects `speeches.parquet` and `transcriptions.parquet` (or a specified transcription file).

```python
from filtering_corpus.speech_corpus import SpeechCorpus

# Load the corpus (default)
corpus = SpeechCorpus()

# Load with a specific transcription file (e.g., cleaned data)
corpus = SpeechCorpus(transcription_file="transcriptions.parquet")
```

## 2. Filtering Methods

The class provides several methods to create a new `SpeechCorpus` instance containing only the filtered data. These methods can be chained or used sequentially.

### By Campaign Cycle

Filter speeches belonging to a specific campaign cycle ('2016', '2020', '2024', or 'Other').

```python
corpus_2016 = corpus.get_campaign("2016")
```

### By Speech Type (Rally)

Filter to keep only rallies or non-rally speeches.

```python
# Get only rallies
rallies = corpus.get_rallies(is_rally=True)

# Get non-rally speeches
other_speeches = corpus.get_rallies(is_rally=False)
```

### By Campaign and Rally Combined

A convenience method to get rallies for a specific campaign.

```python
rallies_2020 = corpus.get_campaign_rallies("2020")
```

### By Location

Filter speeches where the location string contains a specific substring (case-insensitive).

```python
# Get speeches in Pennsylvania
pa_speeches = corpus.get_by_location("PA")
```

### By Category

Filter speeches that have a specific category tag.

```python
# Get speeches related to Economy
economy_speeches = corpus.get_by_category("Economy")
```

### By Date

Filter speeches within a specific date range or remove speeches before a certain year.

```python
# Filter by date range
range_corpus = corpus.filter_date(start_date="2017-01-20", end_date="2021-01-20")

# Remove speeches before 2015
recent_corpus = corpus.remove_speeches_before(2015)
```

### Generic Filter

Apply multiple filters at once using a dictionary.

```python
filters = {
    'campaign': '2016',
    'is_rally': True,
    'location': 'OH'
}
ohio_2016_rallies = corpus.filter(filters)
```

## 3. Getting Full Text for Analysis

Once you have filtered the corpus, you often want to perform analysis on the full text of the speeches. The `get_full_speeches` method aggregates the transcription segments for each speech into a single text block.

```python
# Get a DataFrame with speech metadata and full text
# By default, it aggregates 'text' and 'cleaned_transcription' (if present)
df_speeches = corpus.get_full_speeches()

# Access the full text
print(df_speeches[['title', 'date', 'text_clean']].head())
```

## 4. Saving Sub-Databases

You can save a filtered subset of the corpus to a new directory. This creates new `speeches.parquet` and `transcriptions.parquet` files in the specified subdirectory.

```python
# Save the 2016 rallies to data/rallies_2016
rallies_2016 = corpus.get_campaign_rallies("2016")
rallies_2016.save_sub_db("rallies_2016")
```

## Example Workflow

Here is a complete example of how to use these tools together:

```python
from filtering_corpus.speech_corpus import SpeechCorpus

# 1. Load the cleaned corpus
corpus = SpeechCorpus(transcription_file="transcriptions.parquet")

# 2. Filter for 2024 Campaign Rallies
corpus_2024 = corpus.get_campaign_rallies("2024")

# 3. Get the data for analysis
df = corpus_2024.get_full_speeches()

# 4. Perform analysis (e.g., print count)
print(f"Number of 2024 rallies: {len(df)}")
```
