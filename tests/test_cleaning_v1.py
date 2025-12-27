import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.text_cleaning.cleaner import clean_text

def test_clean_v1_with_stopwords():
    text = '[Audience chants "USA"] Well, that was good timing, wasn\'t it? [Laughs] We had to get that right. We had to get that right, but they always get it right. I was just, uh, given a display with a wonderful first lady, the likes of, which I think few people have ever seen before. We were a few minutes away. And the uh, display of strength was absolutely incredible.'
    
    cleaned = clean_text(
        text,
        remove_stopwords=False,
        remove_punctuation=True,
        lemmatize=True,
        remove_brackets=True
    )
    
    print("Original text:")
    print(text)
    print("\nCleaned text:")
    print(cleaned)
    
    # Assertions
    assert "[Audience chants \"USA\"]" not in cleaned
    assert "[Laughs]" not in cleaned
    assert "?" not in cleaned
    assert "." not in cleaned
    assert "," not in cleaned
    
    # Check for some stopwords being present
    assert "that" in cleaned.split()
    assert "was" not in cleaned.split() # "was" -> "be"
    assert "be" in cleaned.split()
    assert "we" in cleaned.split()
    
    # Check for lemmatization
    assert "minute" in cleaned.split() # minutes -> minute
    assert "see" in cleaned.split() # seen -> see
    
    print("\nTest passed successfully!")

if __name__ == "__main__":
    test_clean_v1_with_stopwords()
