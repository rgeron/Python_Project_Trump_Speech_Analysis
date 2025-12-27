# Transcription Cleaning: Process & Concepts

This document details the process used to clean the speech transcriptions and explains the key concepts and libraries involved.

## The Cleaning Process

We implemented a pipeline to transform raw speech text into a clean, normalized format suitable for analysis. The process involves three main steps:

1.  **Tokenization**: The raw text is split into individual units called "tokens" (words, punctuation, etc.).
2.  **Filtering**: We remove unwanted tokens, specifically:
    - **Punctuation**: Symbols like commas, periods, and exclamation marks.
    - **Stopwords**: Common words that usually carry little meaning (e.g., "and", "the", "is").
3.  **Lemmatization**: We convert the remaining words to their base or dictionary form (e.g., "running" becomes "run").

## Key Concepts

### Tokenization

Tokenization is the process of breaking a stream of text up into words, phrases, symbols, or other meaningful elements called tokens. For example, the sentence "I'm running." might be tokenized into `["I", "'m", "running", "."]`. This is the first step in almost all Natural Language Processing (NLP) tasks.

### Stopwords

Stopwords are words which are filtered out before or after processing of natural language data (text). These are usually the most common words in a language, such as "the", "is", "at", "which", and "on". Removing them helps focus the analysis on the words that carry the most unique content and meaning.

### Lemmatization

Lemmatization is the process of grouping together the inflected forms of a word so they can be analyzed as a single item, identified by the word's lemma, or dictionary form.

- **Example**: "am", "are", "is" $\rightarrow$ "be"
- **Example**: "car", "cars", "car's", "cars'" $\rightarrow$ "car"

Unlike _stemming_, which just chops off the ends of words (often resulting in non-words), lemmatization uses vocabulary and morphological analysis to return the proper base form.

## Libraries Used

### Spacy (`spacy`)

**What it is:** An industrial-strength open-source software library for Advanced Natural Language Processing in Python.
**How we used it:**

- **Tokenization:** We used Spacy's efficient tokenizer to split our text into words.
- **Stopword List:** We utilized Spacy's built-in list of English stopwords to identify which words to filter out.
- **Efficiency:** We disabled heavier components of the Spacy pipeline (like the parser and named entity recognizer) to keep the process fast, as we only needed tokenization.

### Simplemma (`simplemma`)

**What it is:** A simple, lightweight, and language-independent library for lemmatization.
**How we used it:**

- **Lemmatization:** After Spacy tokenized the text and we filtered out the noise, we passed each remaining word to `simplemma` to convert it to its base form.
- **Why Simplemma?** It is lightweight and fast, making it a good choice when you need a specific, simple lemmatizer without the overhead of a full NLP pipeline for that specific step, or if you want to support multiple languages easily in the future.

## Design Choices

1.  **Hybrid Approach**: We combined **Spacy** and **Simplemma**.
    - We used **Spacy** for the initial heavy lifting (tokenization) because it handles edge cases in English text (like "don't" -> "do", "n't") very well.
    - We used **Simplemma** for the actual lemmatization step as requested, ensuring we get the specific behavior of that library.
2.  **Modularity**: We created a dedicated module `src/text_cleaning` instead of writing the code directly in a script. This allows the cleaning logic to be easily imported and reused in other parts of the project (e.g., if we want to clean new speeches as they are scraped).

## How to Run a New Cleaning Version

You can apply different cleaning strategies (e.g., keeping stopwords, changing punctuation rules) and save them as new columns in the main `data/transcriptions.parquet` file. This allows you to compare different preprocessing techniques without duplicating the entire dataset.

### The `apply_cleaning_to_parquet` Function

We have provided a helper function in `src/text_cleaning/cleaner.py` to streamline this process.

```python
from src.text_cleaning.cleaner import apply_cleaning_to_parquet

apply_cleaning_to_parquet(
    parquet_path="data/transcriptions.parquet",
    output_column="cleaned_v2_custom",  # Name of the new column
    remove_stopwords=True,              # Set to False to keep stopwords
    remove_punctuation=True,            # Set to False to keep punctuation
    lemmatize=True,                     # Set to False to keep original word forms
    overwrite=False                     # Set to True to update an existing column
)
```

### Parameters

- **`parquet_path`**: Path to your `transcriptions.parquet` file.
- **`output_column`**: The name of the column where the new cleaned text will be saved. Choose a descriptive name (e.g., `text_no_stops`, `text_lemmatized`).
- **`remove_stopwords`**: (bool) If `True`, removes common English stopwords (e.g., "the", "and").
- **`remove_punctuation`**: (bool) If `True`, removes all punctuation marks.
- **`lemmatize`**: (bool) If `True`, converts words to their base form (e.g., "running" -> "run") using `simplemma`.
- **`overwrite`**: (bool) If `True`, allows the function to overwrite the `output_column` if it already exists. Defaults to `False` to prevent accidental data loss.

### Example Workflow

1.  Open a Python script or Jupyter Notebook.
2.  Import the function: `from src.text_cleaning.cleaner import apply_cleaning_to_parquet`.
3.  Run the function with your desired hyperparameters.
4.  The `data/transcriptions.parquet` file will be updated in place with the new column.
5.  You can then load the data and use the new column for analysis:

```python
import pandas as pd

df = pd.read_parquet("data/transcriptions.parquet")
print(df[['text', 'cleaned_v2_custom']].head())
```
