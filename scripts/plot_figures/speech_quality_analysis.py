import sys
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textstat
import nltk
import ssl
import numpy as np

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "src"))

from filtering_corpus.speech_corpus import SpeechCorpus
from filtering_corpus.other_candidates import OtherCandidatesCorpus

# Create figures directory
figures_dir = project_root / "figures"
figures_dir.mkdir(exist_ok=True)

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (14, 7)

# Fix for NLTK download SSL error
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download necessary NLTK data
nltk.download('cmudict', quiet=True)
nltk.download('punkt', quiet=True)

# ---------------------------------------------------------
# 1. Load and Preprocess Data
# ---------------------------------------------------------
print("Loading corpus...")
# 1. Load Trump Speeches (using clean-v1-with-stopwords)
corpus = SpeechCorpus(data_dir=str(project_root / "data"), transcription_file="transcriptions.parquet")
print(f"Initial Trump Corpus: {corpus}")
# Filter speeches before 2010
corpus = corpus.remove_speeches_before(2010)
print(f"Filtered Trump Corpus: {corpus}")

# Use 'clean-v1-with-stopwords' as the cleaned transcription for Trump, rename to standard 'cleaned_transcription'
df_trump = corpus.get_full_speeches(text_columns=['text', 'clean-v1-with-stopwords'])
df_trump.rename(columns={'clean-v1-with-stopwords': 'cleaned_transcription'}, inplace=True)
df_trump['candidate'] = 'Trump'

# 2. Load Other Candidates
print("Loading other candidates...")
other_corpus = OtherCandidatesCorpus(data_dir=str(project_root / "data"))

# Kamala Harris
kamala_corpus = other_corpus.get_kamala()
# Fetch both text and cleaned_transcription
df_kamala = kamala_corpus.get_full_speeches(text_columns=['text', 'cleaned_transcription'])
df_kamala['candidate'] = 'Harris'
df_kamala['date'] = pd.NaT
df_kamala['title'] = 'Speech: Kamala Harris'
df_kamala['is_rally'] = False

# Joe Biden
biden_corpus = other_corpus.get_biden()
df_biden = biden_corpus.get_full_speeches(text_columns=['text', 'cleaned_transcription'])
df_biden['candidate'] = 'Biden'
df_biden['date'] = pd.NaT
df_biden['title'] = 'Speech: Joe Biden'
df_biden['is_rally'] = False

# 3. Combine All
df = pd.concat([df_trump, df_kamala, df_biden], ignore_index=True)

if 'cleaned_transcription' not in df.columns:
    print("Warning: 'cleaned_transcription' column not found. Lexical diversity analysis will be limited.")
else:
    print("Column 'cleaned_transcription' strictly loaded for all candidates.")

print(f"Total full speeches for analysis: {len(df)}")
print(df['candidate'].value_counts())

# ---------------------------------------------------------
# 2. Calculate Readability Metrics
# ---------------------------------------------------------
def calculate_readability_metrics(text):
    if not isinstance(text, str) or not text.strip():
        return {
            "flesch_kincaid_grade": None,
            "gunning_fog": None,
            "flesch_reading_ease": None
        }
        
    try:
        return {
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
            "flesch_reading_ease": textstat.flesch_reading_ease(text)
        }
    except Exception as e:
        return {
            "flesch_kincaid_grade": None,
            "gunning_fog": None,
            "flesch_reading_ease": None
        }

print("Calculating Flesch-Kincaid and other readability metrics...")
results_readability = df['text'].apply(calculate_readability_metrics)
df_readability = pd.json_normalize(results_readability)

df = pd.concat([df, df_readability], axis=1)
df = df.dropna(subset=['flesch_kincaid_grade'])
df = df[df['flesch_kincaid_grade'] < 100] # Remove outliers

print(f"Successfully processed readability for {len(df)} speeches.")

# Visualization: Readability by Candidate
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='candidate', y='flesch_kincaid_grade', palette="Set2")
plt.title('Flesch-Kincaid Grade Level by Candidate', fontsize=16)
plt.xlabel('Candidate', fontsize=12)
plt.ylabel('Grade Level', fontsize=12)
plt.grid(True, axis='y', alpha=0.3)
plt.savefig(figures_dir / "readability_by_candidate.png")
print(f"Saved readability plot to {figures_dir / 'readability_by_candidate.png'}")

print("Readability Statistics by Candidate:")
print(df.groupby('candidate')['flesch_kincaid_grade'].describe())

# ---------------------------------------------------------
# 3. Lexical Diversity Analysis (CTTR)
# ---------------------------------------------------------
def calculate_lexical_diversity(text):
    if not isinstance(text, str) or not text.strip():
        return {"TTR": None, "CTTR": None}
    
    tokens = text.split()
    total_words = len(tokens)
    unique_words = len(set(tokens))
    
    if total_words == 0:
        return {"TTR": 0, "CTTR": 0}
        
    ttr = unique_words / total_words
    cttr = unique_words / np.sqrt(2 * total_words)
    
    return {"TTR": ttr, "CTTR": cttr}

print("Calculating lexical diversity...")
if 'cleaned_transcription' in df.columns:
    print("Processing cleaned text (lemmatized)...")
    results_diversity_clean = df['cleaned_transcription'].apply(calculate_lexical_diversity)
    df_diversity_clean = pd.json_normalize(results_diversity_clean)
    df_diversity_clean.columns = [f"{col}_clean" for col in df_diversity_clean.columns]
    
    df = pd.concat([df.reset_index(drop=True), df_diversity_clean.reset_index(drop=True)], axis=1)
    df['CTTR'] = df['CTTR_clean']
else:
    print("ERROR: 'cleaned_transcription' column not found.")
    df['CTTR'] = np.nan

print("Processing uncleaned text (for comparison)...")
results_diversity_raw = df['text'].apply(calculate_lexical_diversity)
df_diversity_raw = pd.json_normalize(results_diversity_raw)
df_diversity_raw.columns = [f"{col}_raw" for col in df_diversity_raw.columns]

df = pd.concat([df, df_diversity_raw], axis=1)

# Visualization: CTTR by Candidate
plt.figure(figsize=(14, 6))
sns.violinplot(data=df, x='candidate', y='CTTR', palette="muted", inner="quartile")
plt.title('Distribution of Corrected TTR (CTTR) by Candidate', fontsize=16)
plt.xlabel('Candidate', fontsize=12)
plt.ylabel('CTTR (Cleaned Text)', fontsize=12)
plt.grid(True, axis='y', alpha=0.3)
plt.savefig(figures_dir / "cttr_by_candidate.png")
print(f"Saved CTTR plot to {figures_dir / 'cttr_by_candidate.png'}")

print("CTTR Statistics by Candidate:")
print(df.groupby('candidate')['CTTR'].describe())

print("Analysis Complete.")
