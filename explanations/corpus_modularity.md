# Corpus Modularity

This codebase allows for flexible analysis of speeches from different political candidates by using modular corpus classes.

## The Two Corpus Classes

1.  **`SpeechCorpus`** (`src/filtering_corpus/speech_corpus.py`):

    - **Focus**: Donald Trump.
    - **Data Source**: `data/speeches.parquet` and `data/transcriptions.parquet`.
    - **Metadata**: Rich metadata including Date, Location, Rally vs Non-Rally, Campaign Cycle, etc.
    - **Filtering**: Advanced filtering by campaign, rally, location, date, category.

2.  **`OtherCandidatesCorpus`** (`src/filtering_corpus/other_candidates.py`):
    - **Focus**: Kamala Harris, Joe Biden, and potentially others.
    - **Data Source**: `data/other_transcriptions.parquet`.
    - **Metadata**: Minimal (Candidate Name only currently).
    - **Filtering**: Simple filtering by candidate name.

## Combining Corpora for Analysis

To perform comparative analysis (e.g., comparing Trump vs Harris), you can easily load both corpora and combine them into a single pandas DataFrame.

The `OtherCandidatesCorpus.get_full_speeches()` method has been updated to return a format compatible with `SpeechCorpus.get_full_speeches()`, filling missing metadata with placeholders (e.g., `date` is `NaT`, `is_rally` is `False`).

### Example Usage

```python
import pandas as pd
from src.filtering_corpus.speech_corpus import SpeechCorpus
from src.filtering_corpus.other_candidates import OtherCandidatesCorpus

# 1. Load Trump Data
trump_corpus = SpeechCorpus(data_dir="data")
# Optional: Filter Trump data first
trump_corpus = trump_corpus.remove_speeches_before(2016)
df_trump = trump_corpus.get_full_speeches()
df_trump['candidate'] = 'Trump' # Explicitly label

# 2. Load Other Candidates
other_corpus = OtherCandidatesCorpus(data_dir="data")

# Load Harris
kamala_corpus = other_corpus.get_kamala()
df_kamala = kamala_corpus.get_full_speeches()
# 'candidate' column is automatically populated as 'Kamala Harris' or derived

# Load Biden
biden_corpus = other_corpus.get_biden()
df_biden = biden_corpus.get_full_speeches()

# 3. Combine
df_all = pd.concat([df_trump, df_kamala, df_biden], ignore_index=True)

# 4. Analyze
# Now you can analyze df_all grouping by 'candidate'
print(df_all.groupby('candidate').size())
```

## Adding New Candidates

If `data/other_transcriptions.parquet` is updated with more candidates, you can access them generically:

```python
# Get a generic candidate by name
new_candidate_corpus = other_corpus.get_candidate("New Candidate Name")
df_new = new_candidate_corpus.get_full_speeches()
```
