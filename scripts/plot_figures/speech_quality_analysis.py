import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textstat
import nltk
import ssl

# -------------------------------------------------------------------
# Configuration générale
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from filtering_corpus.speech_corpus import SpeechCorpus
from filtering_corpus.other_candidates import OtherCandidatesCorpus

FIGURES_DIR = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (14, 7)

# Correctif SSL pour le téléchargement NLTK
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

nltk.download("cmudict", quiet=True)
nltk.download("punkt", quiet=True)


# -------------------------------------------------------------------
# Chargement des données
# -------------------------------------------------------------------

def load_data():
    """
    Charge et rassemble les discours de Trump, Harris et Biden
    dans un seul DataFrame.
    """
    data_dir = PROJECT_ROOT / "data"

    # Trump
    trump_corpus = SpeechCorpus(
        data_dir=str(data_dir),
        transcription_file="transcriptions.parquet"
    ).remove_speeches_before(2010)

    df_trump = trump_corpus.get_full_speeches(
        text_columns=["text", "text_lemmatized"]
    )
    df_trump["candidate"] = "Trump"

    # Autres candidats
    other_corpus = OtherCandidatesCorpus(data_dir=str(data_dir))

    kamala = other_corpus.get_kamala().get_full_speeches(
        text_columns=["text", "text_lemmatized"]
    )
    kamala["candidate"] = "Harris"

    biden = other_corpus.get_biden().get_full_speeches(
        text_columns=["text", "text_lemmatized"]
    )
    biden["candidate"] = "Biden"

    return pd.concat([df_trump, kamala, biden], ignore_index=True)


# -------------------------------------------------------------------
# Lisibilité
# -------------------------------------------------------------------

def readability_metrics(text):
    """
    Calcule les scores de lisibilité principaux.
    """
    return {
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text),
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
    }


def process_readability(df):
    """
    Ajoute les métriques de lisibilité et enlève les valeurs aberrantes.
    """
    metrics = df["text"].apply(readability_metrics)
    metrics_df = pd.json_normalize(metrics)

    df = pd.concat([df.reset_index(drop=True), metrics_df], axis=1)
    df = df[df["flesch_kincaid_grade"] < 100]

    return df


def plot_readability(df):
    """
    Boxplot du score Flesch-Kincaid par candidat.
    """
    plt.figure()
    sns.boxplot(
        data=df,
        x="candidate",
        y="flesch_kincaid_grade",
        palette="Set2"
    )
    plt.title("Lisibilité (Flesch-Kincaid) par candidat")
    plt.xlabel("Candidat")
    plt.ylabel("Niveau scolaire")
    plt.grid(axis="y", alpha=0.3)
    plt.savefig(FIGURES_DIR / "readability_by_candidate.png")
    plt.close()


# -------------------------------------------------------------------
# Diversité lexicale
# -------------------------------------------------------------------

def lexical_diversity(text):
    """
    Calcule le TTR et le CTTR.
    """
    tokens = text.split()
    n_tokens = len(tokens)
    n_types = len(set(tokens))

    return {
        "TTR": n_types / n_tokens,
        "CTTR": n_types / np.sqrt(2 * n_tokens)
    }


def process_lexical_diversity(df):
    """
    Calcule la diversité lexicale sur le texte lemmatisé.
    """
    diversity = df["text_lemmatized"].apply(lexical_diversity)
    diversity_df = pd.json_normalize(diversity)

    return pd.concat([df.reset_index(drop=True), diversity_df], axis=1)


def plot_lexical_diversity(df):
    """
    Distribution du CTTR par candidat.
    """
    plt.figure()
    sns.violinplot(
        data=df,
        x="candidate",
        y="CTTR",
        palette="muted",
        inner="quartile"
    )
    plt.title("Diversité lexicale (CTTR) par candidat")
    plt.xlabel("Candidat")
    plt.ylabel("CTTR")
    plt.grid(axis="y", alpha=0.3)
    plt.savefig(FIGURES_DIR / "cttr_by_candidate.png")
    plt.close()


# -------------------------------------------------------------------
# Script principal
# -------------------------------------------------------------------

def main():
    df = load_data()

    df = process_readability(df)
    plot_readability(df)

    print("\nLisibilité moyenne :")
    print(df.groupby("candidate")["flesch_kincaid_grade"].describe())

    df = process_lexical_diversity(df)
    plot_lexical_diversity(df)

    print("\nDiversité lexicale :")
    print(df.groupby("candidate")["CTTR"].describe())


if __name__ == "__main__":
    main()
