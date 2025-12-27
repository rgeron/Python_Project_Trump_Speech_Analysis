from pathlib import Path
import sqlite3
import pandas as pd

def convert_sqlite_to_parquet(db_path="data/speeches.db", output_dir="data"):
    """
    Converts Speeches and Transcriptions tables from SQLite to Parquet files.
    """
    conn = sqlite3.connect(db_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert Speeches
    df_speeches = pd.read_sql_query("SELECT * FROM Speeches", conn)
    
    # Clean numeric columns that might contain empty strings
    numeric_cols = ['nbr_sentences', 'nbr_words', 'nbr_seconds']
    for col in numeric_cols:
        if col in df_speeches.columns:
            df_speeches[col] = pd.to_numeric(df_speeches[col], errors='coerce')
            
    df_speeches.to_parquet(output_path / "speeches.parquet", index=False)

    # Convert Transcriptions
    df_transcriptions = pd.read_sql_query("SELECT * FROM Transcriptions", conn)
    
    # Clean numeric columns in Transcriptions
    if 'speech_id' in df_transcriptions.columns:
         df_transcriptions['speech_id'] = pd.to_numeric(df_transcriptions['speech_id'], errors='coerce')
         
    transcriptions_file = output_path / "transcriptions.parquet"
    if transcriptions_file.exists():
        existing_df = pd.read_parquet(transcriptions_file)
        # Identify extra columns in existing file (e.g. cleaned text columns)
        extra_cols = [col for col in existing_df.columns if col not in df_transcriptions.columns]
        if extra_cols:
            print(f"Preserving existing columns: {extra_cols}")
            # Merge extra columns based on 'id'
            # We use left join to keep all new rows, and fill missing with NaN
            if 'id' in df_transcriptions.columns and 'id' in existing_df.columns:
                df_transcriptions = df_transcriptions.merge(
                    existing_df[['id'] + extra_cols],
                    on='id',
                    how='left'
                )
            else:
                print("Warning: 'id' column missing. Cannot preserve extra columns.")

    df_transcriptions.to_parquet(transcriptions_file, index=False)
    
    conn.close()