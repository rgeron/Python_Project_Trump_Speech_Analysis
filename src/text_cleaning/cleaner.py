import re
import spacy
import simplemma
import pandas as pd
from pathlib import Path
from typing import List, Optional

# Load spacy model globally to avoid reloading it multiple times
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load('en_core_web_sm')

def basic_normalization(text: str) -> str:
    """
    Step 1: Basic Normalization
    - Convert to lowercase
    - Remove punctuation
    - Preserve word order
    - Do NOT remove stopwords
    - Do NOT lemmatize
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation using regex (more efficient than spacy for just this)
    # We want to preserve spaces between words, so we replace punct with nothing
    # but we need to be careful. If we have "word.word", replacing '.' might merge them.
    # Usually it's safer to rely on tokenization for punct removal, but the requirement says:
    # "Convert text to lowercase, Remove punctuation, Preserve word order"
    # A simple regex approach for standard punctuation:
    # We can use spacy to be safe about token boundaries if performance allows, 
    # but for "Basic Normalization" strictly:
    
    # Let's use spacy for consistency with the rest of the project, 
    # but enable only tokenizer.
    # Actually, the user asked to disable unnecessary components for performance.
    
    doc = nlp(text, disable=['parser', 'ner', 'textcat', 'lemmatizer', 'tagger'])
    tokens = [token.text for token in doc if not token.is_punct]
    return " ".join(tokens)

def token_cleaning(text: str) -> str:
    """
    Step 2: Token Cleaning
    - Tokenize (already done implicitly if input is string)
    - Remove stopwords
    - Remove empty or non-alphabetic tokens
    """
    if not text:
        return ""
    
    doc = nlp(text, disable=['parser', 'ner', 'textcat', 'lemmatizer', 'tagger'])
    stopwords = nlp.Defaults.stop_words
    
    tokens = []
    for token in doc:
        if token.is_space:
            continue
        if not token.is_alpha: # Remove non-alphabetic
             continue
        if token.text.lower() in stopwords: # Remove stopwords
            continue
            
        tokens.append(token.text)
        
    return " ".join(tokens)

def lemmatization(text: str) -> str:
    """
    Step 3: Lemmatization
    - Lemmatize tokens using simplemma
    """
    if not text:
        return ""
    
    # We assume text is already space-separated tokens from previous steps
    # But simplemma needs words.
    
    tokens = text.split()
    lemmatized_tokens = [simplemma.lemmatize(token, lang='en') for token in tokens]
    
    return " ".join(lemmatized_tokens)

# Keep existing functions for backward compatibility or refactor if needed.
# For now, we leave them as is or slightly modify them to use the new steps if appropriate,
# but the user didn't strictly ask to remove the old one, just to "Implement the logic in a dedicated module".
# The old `clean_text` does all at once.

def clean_text(
    text: str,
    remove_stopwords: bool = True,
    remove_punctuation: bool = True,
    lemmatize: bool = True,
    remove_brackets: bool = False
) -> str:
    """
    Cleans a single text string by tokenizing, optionally removing stopwords/punctuation,
    removing text in brackets, and lemmatizing with simplemma.
    """
    if not text:
        return ""

    # Remove text between brackets if requested
    if remove_brackets:
        text = re.sub(r'\[.*?\]', '', text)

    # Tokenize with spacy (disable unnecessary components for speed)
    doc = nlp(text, disable=['parser', 'ner', 'textcat'])
    
    stopwords = nlp.Defaults.stop_words
    
    tokens = []
    for token in doc:
        # Skip punctuation if requested
        if remove_punctuation and token.is_punct:
            continue
            
        # Skip stopwords if requested
        if remove_stopwords and token.text.lower() in stopwords:
            continue
            
        # Skip whitespace
        if token.is_space:
            continue
            
        word = token.text.lower()
        
        # Lemmatize if requested
        if lemmatize:
            # simplemma.lemmatize returns the lemma
            lemma = simplemma.lemmatize(word, lang='en')
            tokens.append(lemma)
        else:
            tokens.append(word)
            
    return " ".join(tokens)

def clean_docs(
    texts: List[str],
    remove_stopwords: bool = True,
    remove_punctuation: bool = True,
    lemmatize: bool = True,
    remove_brackets: bool = False,
    n_process: int = 1,
    batch_size: int = 100
) -> List[str]:
    """
    Cleans a list of documents.
    """
    cleaned_texts = []
    
    if remove_brackets:
        texts = [re.sub(r'\[.*?\]', '', t) if t else "" for t in texts]

    # Use nlp.pipe only if we are generic cleaning. 
    # For specialized steps, we might want specialized batch functions 
    # but for now we keep this old function as is.
    docs = nlp.pipe(texts, n_process=n_process, batch_size=batch_size, disable=['parser', 'ner', 'textcat'])
    
    stopwords = nlp.Defaults.stop_words
    
    for doc in docs:
        tokens = []
        for token in doc:
            if remove_punctuation and token.is_punct:
                continue
            if remove_stopwords and token.text.lower() in stopwords:
                continue
            if token.is_space:
                continue
                
            word = token.text.lower()
            if lemmatize:
                tokens.append(simplemma.lemmatize(word, lang='en'))
            else:
                tokens.append(word)
        cleaned_texts.append(" ".join(tokens))
        
    return cleaned_texts

def apply_cleaning_to_parquet(
    parquet_path: str,
    output_column: str,
    remove_stopwords: bool = True,
    remove_punctuation: bool = True,
    lemmatize: bool = True,
    remove_brackets: bool = False,
    overwrite: bool = False
):
    """
    Legacy function: Applies text cleaning to the 'text' column of a parquet file.
    """
    path = Path(parquet_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
        
    df = pd.read_parquet(path)
    
    if 'text' not in df.columns:
        raise ValueError("Parquet file must contain a 'text' column")
        
    if output_column in df.columns and not overwrite:
        print(f"Column '{output_column}' already exists. Skipping. Set overwrite=True to force update.")
        return
        
    print(f"Cleaning text for column '{output_column}'...")
    cleaned_texts = clean_docs(
        df['text'].fillna("").tolist(),
        remove_stopwords=remove_stopwords,
        remove_punctuation=remove_punctuation,
        lemmatize=lemmatize,
        remove_brackets=remove_brackets
    )
    
    df[output_column] = cleaned_texts
    
    df.to_parquet(path, index=False)
    print(f"Saved updated parquet to {path}")

