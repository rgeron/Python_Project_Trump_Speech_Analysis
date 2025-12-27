import sys
import pandas as pd
from pathlib import Path
import logging

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.text_cleaning.cleaner import clean_docs


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import argparse

def main():
    parser = argparse.ArgumentParser(description='Clean transcriptions for a candidate.')
    parser.add_argument('--candidate', type=str, default='trump', choices=['trump', 'harris', 'biden'], help='Candidate to process (trump, harris, or biden)')
    parser.add_argument('--colname', type=str, default='cleaned_transcription', help='Name of the output column')
    args = parser.parse_args()

    candidate = args.candidate.lower()
    col_name = args.colname
    
    data_dir = project_root / 'data'
    
    if candidate == 'trump':
        input_file = data_dir / 'transcriptions.parquet'
        output_file = input_file
    elif candidate in ['harris', 'biden']:
        input_file = data_dir / 'other_transcriptions.parquet'
        output_file = input_file
    else:
        print(f"Unknown candidate: {candidate}")
        return

    print(f"Cleaning transcriptions for {candidate} from {input_file} to {output_file}")

    if not input_file.exists():
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)

    logging.info(f"Reading transcriptions from {input_file}")
    df = pd.read_parquet(input_file)

    if 'text' not in df.columns:
        sys.exit(1)

    logging.info("Cleaning transcriptions...")
    texts = df['text'].fillna("").astype(str).tolist()
    cleaned_texts = clean_docs(texts, n_process=4)
        
    # Add to dataframe
    df[col_name] = cleaned_texts
    
    # Save to new parquet
    logging.info(f"Saving cleaned transcriptions to {output_file}")
    df.to_parquet(output_file)
    logging.info("Done.")

if __name__ == "__main__":
    main()
