from pathlib import Path
import sqlite3, json, re
import pandas as pd
import spacy

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "speeches.db"
OUTPUT = DATA_DIR / "cleaned_tokens.json"

nlp = spacy.load("en_core_web_sm")

def load_transcriptions():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT text FROM Transcriptions", conn)["text"]

def build_clean_text(phrases):
    pieces = []
    for phrase in phrases.dropna():
        chunks = [re.sub(r"\[.*?\]", "", part).strip()
                  for part in re.split(r"[.!?]+", str(phrase))]
        pieces.extend(filter(None, chunks))
    return " ".join(pieces)

def tokenize(text):
    return [tok.lemma_ for tok in nlp(text)
            if not tok.is_punct and not tok.is_stop]

def main():
    phrases = load_transcriptions()
    clean_text = build_clean_text(phrases)
    cleaned_tokens = tokenize(clean_text)
    OUTPUT.write_text(json.dumps(cleaned_tokens, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()