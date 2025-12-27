import sys
import os
sys.path.append(os.getcwd())
from src.text_cleaning.cleaner import basic_normalization

text = "Ladies and gentlemen [APPLAUSE], welcome!"
cleaned = basic_normalization(text)
print(f"Original: {text}")
print(f"Cleaned: '{cleaned}'")

if "[APPLAUSE]" not in cleaned and "ladies" in cleaned:
    print("SUCCESS: Brackets removed.")
else:
    print("FAILED: Brackets NOT removed.")
