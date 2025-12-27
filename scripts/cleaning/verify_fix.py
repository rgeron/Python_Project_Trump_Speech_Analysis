import pandas as pd
import re

df = pd.read_parquet('data/transcriptions.parquet')
# Check for brackets in text_basic
matches = df[df['text_basic'].str.contains(r'\[.*?\]', regex=True, na=False)]
if not matches.empty:
    print(f"FAILED: Found {len(matches)} rows with brackets in text_basic:")
    print(matches['text_basic'].head())
else:
    print("SUCCESS: No brackets found in text_basic.")
    
# Also check for 'applause' if it was inside brackets usually
# Though applause might appear outside, we expect [APPLAUSE] to be gone.
print("Sample text_basic:")
print(df['text_basic'].sample(5).values)
