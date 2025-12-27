
import pandas as pd
from src.filtering_corpus.speech_corpus import SpeechCorpus

corpus = SpeechCorpus()
df = corpus.get_full_speeches()
print(df['categories'].head(10))
print(f"Type of first category: {type(df['categories'].iloc[0])}")
