import sqlite3
import pandas as pd
from pathlib import Path

def init_db(db_path="data/speeches.db"):
    conn = sqlite3.connect(db_path)
    # Table Speeches
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Speeches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            date TEXT,
            nbr_sentences INTEGER,
            nbr_words INTEGER,
            nbr_seconds INTEGER,
            categories TEXT,
            person_name TEXT
        );
    """)

    # Table Transcriptions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            speech_id INTEGER NOT NULL,
            timestamp TEXT,
            duration TEXT,
            text TEXT,
            FOREIGN KEY (speech_id) REFERENCES Speeches(id)
        );
    """)
    conn.commit()
    return conn

def add_speech_to_parquet(speech_data, transcription_data, output_dir="data", file_prefix=""):
    """
    Appends a new speech and its transcription to the existing Parquet files.
    If files don't exist, creates them.
    
    Args:
        speech_data (dict): Dictionary containing speech data
        transcription_data (dict): Dictionary containing transcription data
        output_dir (str): Directory where parquet files are stored
    """
    output_path = Path(output_dir)
    speeches_filename = f"{file_prefix}speeches.parquet" if file_prefix else "speeches.parquet"
    transcriptions_filename = f"{file_prefix}transcriptions.parquet" if file_prefix else "transcriptions.parquet"
    
    speeches_file = output_path / speeches_filename
    transcriptions_file = output_path / transcriptions_filename
    
    # Process Speech
    new_speech_df = pd.DataFrame([speech_data])
    
    # Ensure numeric columns are actually numeric
    numeric_cols = ['nbr_sentences', 'nbr_words', 'nbr_seconds']
    for col in numeric_cols:
        if col in new_speech_df.columns:
            new_speech_df[col] = pd.to_numeric(new_speech_df[col], errors='coerce')
            
    if speeches_file.exists():
        existing_speeches = pd.read_parquet(speeches_file)
        updated_speeches = pd.concat([existing_speeches, new_speech_df], ignore_index=True)
    else:
        updated_speeches = new_speech_df
    updated_speeches.to_parquet(speeches_file, index=False)
    
    # Process Transcription
    if isinstance(transcription_data, list):
        new_transcription_df = pd.DataFrame(transcription_data)
    else:
        new_transcription_df = pd.DataFrame([transcription_data])
    if transcriptions_file.exists():
        existing_transcriptions = pd.read_parquet(transcriptions_file)
        updated_transcriptions = pd.concat([existing_transcriptions, new_transcription_df], ignore_index=True)
    else:
        updated_transcriptions = new_transcription_df
    updated_transcriptions.to_parquet(transcriptions_file, index=False)
