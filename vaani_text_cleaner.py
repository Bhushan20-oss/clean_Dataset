"""
Custom text cleaning for Vaani dataset.
Handles English translations in curly braces and special tokens.
"""

import re


def clean_vaani_transcript(text: str) -> str:
    """
    Clean Vaani transcripts by removing English translations and special tokens.
    
    Examples:
        Input:  "एक वॉचमन {watchman} असा तचा साइडीन {side} एक"
        Output: "एक वॉचमन असा तचा साइडीन एक"
        
        Input:  "दोन बुरगे असा एक बुर्ग्यान <pause> ब्लू कलरचो शर्ट {blue color shirt} घा --</pause>"
        Output: "दोन बुरगे असा एक बुर्ग्यान ब्लू कलरचो शर्ट घा"
    
    Args:
        text: Input transcript text
        
    Returns:
        Cleaned text with English translations and special tokens removed
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove English translations in curly braces: {watchman}, {side}, etc.
    text = re.sub(r'\{[^}]*\}', '', text)
    
    # Remove special tokens: <pause>, </pause>, <noise>, etc.
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove extra punctuation like -- that might be left over
    text = re.sub(r'--+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_vaani_transcript(text: str, remove_punctuation: bool = False) -> str:
    """
    Normalize Vaani transcript text.
    
    Args:
        text: Input text
        remove_punctuation: Whether to remove Devanagari punctuation
        
    Returns:
        Normalized text, or empty string if invalid
    """
    # First clean special patterns
    text = clean_vaani_transcript(text)
    
    if not text:
        return ""
    
    # Optional: Remove Devanagari punctuation if requested
    if remove_punctuation:
        # Devanagari punctuation marks
        devanagari_punct = '।॥?!,;:.\'"'
        for punct in devanagari_punct:
            text = text.replace(punct, '')
    
    # Remove extra whitespace again
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def batch_clean_vaani_transcripts(batch: dict, text_column: str = "transcript") -> dict:
    """
    Clean Vaani transcripts in a batch.
    
    Args:
        batch: Dictionary of lists (batch format)
        text_column: Name of the transcript column
        
    Returns:
        Batch with cleaned transcripts
    """
    cleaned_texts = []
    
    for text in batch[text_column]:
        cleaned = normalize_vaani_transcript(text, remove_punctuation=False)
        cleaned_texts.append(cleaned if cleaned else "")
    
    batch[text_column] = cleaned_texts
    return batch


# Test examples
if __name__ == "__main__":
    print("Testing Vaani text cleaning:\n")
    
    test_cases = [
        "एक वॉचमन {watchman} असा तचा साइडीन {side} एक",
        "दोन बुरगे असा एक बुर्ग्यान <pause> ब्लू कलरचो शर्ट {blue color shirt} घा --</pause>",
        "सामान्य वाक्य बिना कोई special tokens",
        "{english only} should be removed",
        "<pause> <noise> only tokens </pause>",
        "मिक्स्ड {mixed} <tag> कंटेंट -- यहां",
    ]
    
    for i, test in enumerate(test_cases, 1):
        cleaned = clean_vaani_transcript(test)
        print(f"{i}. Original: {test}")
        print(f"   Cleaned:  {cleaned}")
        print()

