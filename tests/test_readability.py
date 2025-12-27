import sys
from pathlib import Path
import pandas as pd
import textstat
import nltk
import ssl

# Add src to path
project_root = Path(".").resolve()
sys.path.append(str(project_root / "src"))

from filtering_corpus.speech_corpus import SpeechCorpus

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('cmudict')
nltk.download('punkt')


def calculate_readability_metrics(text):
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        return {
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
            "flesch_reading_ease": textstat.flesch_reading_ease(text)
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Loading corpus...")
corpus = SpeechCorpus(data_dir="data")
print(f"Corpus loaded: {corpus}")

print("Filtering speeches before 2010...")
corpus = corpus.remove_speeches_before(2010)
print(f"Filtered corpus: {corpus}")

print("Getting full speeches...")
full_speeches = corpus.get_full_speeches()
print(f"Total full speeches: {len(full_speeches)}")

print("Testing on first 5 speeches...")
subset = full_speeches.head(5).copy()
results = subset['text'].apply(calculate_readability_metrics)
print(pd.json_normalize(results))
print("Test complete.")
