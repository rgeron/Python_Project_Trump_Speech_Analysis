import pandas as pd
from pathlib import Path

data_dir = Path("data")
files = ['transcriptions.parquet', 'other_transcriptions.parquet']

for f in files:
    path = data_dir / f
    if path.exists():
        df = pd.read_parquet(path)
        print(f"\n--- {f} ---")
        print(f"Columns: {df.columns.tolist()}")
        if 'text_lemmatized' in df.columns:
            print("Sample of text_lemmatized:")
            print(df[['text', 'text_lemmatized']].head(3))
    else:
        print(f"{f} not found")
