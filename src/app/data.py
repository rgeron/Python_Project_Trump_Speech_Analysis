
import streamlit as st
import pandas as pd
from src.filtering_corpus.speech_corpus import SpeechCorpus

# --- Constants ---
ANALYSIS_COLUMNS = [
    'text', 
    'text_basic',
    'text_no_stopwords',
    'text_lemmatized',
]

@st.cache_data
def load_data():
    """
    Loads the speech corpus and aggregates transcriptions.
    Returns:
        pd.DataFrame: A dataframe containing merged speech metadata and text.
    """
    # Initialize the corpus
    corpus = SpeechCorpus()
    
    # Get full speeches with the specified text columns
    try:
        df = corpus.get_full_speeches(text_columns=ANALYSIS_COLUMNS)
    except Exception as e:
        # Fallback if some columns are missing, though get_full_speeches checks this.
        # We can try to load with available columns or just raise.
        raise e
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Parse categories from string to list
    import ast
    def parse_categories(x):
        try:
            val = ast.literal_eval(x)
            if isinstance(val, list):
                return val
            return ["Uncategorized"]
        except:
            return ["Uncategorized"]

    df['categories'] = df['categories'].fillna('["Uncategorized"]').apply(parse_categories)
    
    # Fill NaN location/campaign for cleaner UI
    df['location'] = df['location'].fillna('Unknown')
    df['campaign'] = df['campaign'].fillna('Other')
    
    # Create a nice label for selection in Inspector
    df['label'] = df['date'].dt.strftime('%Y-%m-%d') + " - " + df['location'] + " (" + df['title'].str[:30] + "...)"

    return df
