import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from collections import Counter

class TextDataset(Dataset):
    def __init__(self, parquet_path, sequence_length=10, max_vocab_size=5000):
        self.sequence_length = sequence_length
        try:
            df = pd.read_parquet(parquet_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find file at {parquet_path}")
        text_data = df['text'].dropna().str.lower().tolist()
        self.full_text = " ".join(text_data)
        self.words = self.full_text.split()
        word_counts = Counter(self.words)
        self.vocab = sorted(word_counts, key=word_counts.get, reverse=True)[:max_vocab_size]
        self.word_to_int = {word: i for i, word in enumerate(self.vocab)}
        self.int_to_word = {i: word for word, i in self.word_to_int.items()}
        self.encoded_text = [self.word_to_int[word] for word in self.words if word in self.word_to_int]
        
    def __len__(self):
        return len(self.encoded_text) - self.sequence_length

    def __getitem__(self, idx):
        x_seq = self.encoded_text[idx : idx + self.sequence_length]
        y_seq = self.encoded_text[idx + self.sequence_length]
        
        return torch.tensor(x_seq, dtype=torch.long), torch.tensor(y_seq, dtype=torch.long)

def get_vocab_size(dataset):
    return len(dataset.vocab)
