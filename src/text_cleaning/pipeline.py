import pandas as pd
from pathlib import Path
from typing import Callable, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def apply_processing_step(
    parquet_path: str,
    input_col: str,
    output_col: str,
    step_func: Callable[[str], str],
    overwrite: bool = False,
    **kwargs
):
    """
    Applies a processing step to a column in a parquet file and saves the result to a new column.
    
    Args:
        parquet_path (str): Path to the parquet file.
        input_col (str): Name of the input column.
        output_col (str): Name of the output column.
        step_func (Callable): Function to apply to each element of the input column.
        overwrite (bool): Whether to overwrite the output column if it already exists.
        **kwargs: Additional arguments to pass to step_func (not used currently but good for extensibility).
    """
    path = Path(parquet_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
        
    logging.info(f"Reading {path}...")
    df = pd.read_parquet(path)
    
    if input_col not in df.columns:
        raise ValueError(f"Input column '{input_col}' not found in {path}. Available columns: {df.columns.tolist()}")
        
    if output_col in df.columns and not overwrite:
        logging.info(f"Column '{output_col}' already exists. Skipping. Set overwrite=True to force update.")
        return

    logging.info(f"Applying processing step: {input_col} -> {output_col}")
    
    # Apply the function. 
    # We use basic apply for simplicity. For massive datasets, nlp.pipe in batches would be faster,
    # but our step functions (like basic_normalization) assume single string input.
    # Given the requirements, this loop is acceptable.
    # We handlle NaNs by treating them as empty strings.
    
    # Helper to apply safely
    def safe_apply(text):
        if pd.isna(text):
            return ""
        return step_func(str(text))
        
    df[output_col] = df[input_col].apply(safe_apply)
    
    logging.info(f"Saving updated parquet at {path}...")
    df.to_parquet(path, index=False)
    logging.info("Done.")
