import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.text_cleaning.cleaner import apply_cleaning_to_parquet

def main():
    parquet_path = "data/transcriptions.parquet"
    output_column = "clean-v1-with-stopwords"
    
    print(f"Applying cleaning to {parquet_path}...")
    print(f"Output column: {output_column}")
    
    apply_cleaning_to_parquet(
        parquet_path=parquet_path,
        output_column=output_column,
        remove_stopwords=False,
        remove_punctuation=True,
        lemmatize=True,
        remove_brackets=True,
        overwrite=True
    )
    
    print("Done!")

if __name__ == "__main__":
    main()
