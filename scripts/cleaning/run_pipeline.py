import sys
from pathlib import Path
import logging
import argparse

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.text_cleaning.cleaner import basic_normalization, token_cleaning, lemmatization
from src.text_cleaning.pipeline import apply_processing_step

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(target_files, overwrite=False):
    """
    Runs the 3-step cleaning pipeline on the target files.
    """
    
    # Define pipeline steps
    steps = [
        {
            "name": "Step 1: Basic Normalization",
            "input_col": "text",
            "output_col": "text_basic",
            "func": basic_normalization
        },
        {
            "name": "Step 2: Token Cleaning",
            "input_col": "text_basic",
            "output_col": "text_no_stopwords",
            "func": token_cleaning
        },
        {
            "name": "Step 3: Lemmatization",
            "input_col": "text_no_stopwords",
            "output_col": "text_lemmatized",
            "func": lemmatization
        }
    ]
    
    data_dir = project_root / 'data'
    
    for filename in target_files:
        filepath = data_dir / filename
        if not filepath.exists():
            logging.error(f"File not found: {filepath}")
            continue
            
        logging.info(f"Processing file: {filename}")
        
        for step in steps:
            logging.info(f"--- {step['name']} ---")
            apply_processing_step(
                parquet_path=str(filepath),
                input_col=step['input_col'],
                output_col=step['output_col'],
                step_func=step['func'],
                overwrite=overwrite
            )
            
    logging.info("Pipeline completed for all files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run text cleaning pipeline.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing columns.')
    args = parser.parse_args()
    
    target_files = ['transcriptions.parquet', 'other_transcriptions.parquet']
    
    run_pipeline(target_files, overwrite=args.overwrite)
