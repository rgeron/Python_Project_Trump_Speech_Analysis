import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.text_cleaning.cleaner import basic_normalization, token_cleaning, lemmatization

def test_cleaning():
    sample_text = "Hello, World! This is a TEST with 123 numbers and some StopWords."
    
    print(f"Original: {sample_text}\n")
    
    # Step 1
    step1 = basic_normalization(sample_text)
    print(f"Step 1 (Basic): {step1}")
    # Expect: hello world this is a test with 123 numbers and some stopwords
    
    # Step 2
    step2 = token_cleaning(step1)
    print(f"Step 2 (Token): {step2}")
    # Expect: hello world test numbers stopwords (stopwords removed, 'is', 'a', 'this', 'some', 'with' probably removed)
    
    # Step 3
    # Let's try something that needs lemmatization
    sample_lemma_text = "tokens running fast"
    step3_input = token_cleaning(basic_normalization(sample_lemma_text))
    step3 = lemmatization(step3_input)
    print(f"\nLemma Input: {sample_lemma_text}")
    print(f"Step 3 (Lemma): {step3}")
    # Expect: token run fast (or similar)

if __name__ == "__main__":
    test_cleaning()
