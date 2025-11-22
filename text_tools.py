"""
Text normalization utilities for ASR dataset preparation.
Based on omnilingual-asr pipeline.
"""

import re
import unicodedata
from typing import Optional


# Language-specific punctuation to remove
PUNCTUATION_PATTERNS = {
    'default': r'[!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]',
    'zh': r'[!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~。，、；：？！…—·ˉ¨''""々～‖∶＂＇｀｜〃〔〕〈〉《》「」『』．〖〗【】（）［］｛｝]',
    'ja': r'[!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~。、・；：？！…ー～〜「」『』（）｛｝［］【】《》〈〉〔〕]',
    'ko': r'[!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~。、；：？！…—～·ㆍ「」『』（）｛｝［］【】《》〈〉〔〕]',
}


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters to composed form (NFC).
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    return unicodedata.normalize('NFC', text)


def remove_punctuation(text: str, language_code: str = 'default') -> str:
    """
    Remove punctuation from text based on language.
    
    Args:
        text: Input text
        language_code: ISO language code (e.g., 'en', 'zh', 'ja', 'ko')
        
    Returns:
        Text without punctuation
    """
    # Get language-specific pattern or use default
    lang_key = language_code.split('_')[0].lower()
    pattern = PUNCTUATION_PATTERNS.get(lang_key, PUNCTUATION_PATTERNS['default'])
    
    return re.sub(pattern, '', text)


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace (multiple spaces, tabs, newlines).
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def remove_digit_only_words(text: str) -> bool:
    """
    Check if text should be filtered (contains only digits).
    
    Args:
        text: Input text
        
    Returns:
        True if text should be kept, False if it should be filtered
    """
    # Remove whitespace and check if only digits remain
    text_no_space = text.replace(' ', '')
    if text_no_space and text_no_space.isdigit():
        return False
    return True


def remove_brackets_content(text: str) -> str:
    """
    Remove content within brackets (useful for removing annotations).
    
    Args:
        text: Input text
        
    Returns:
        Text without bracketed content
    """
    # Remove content within square brackets
    text = re.sub(r'\[.*?\]', '', text)
    # Remove content within angle brackets
    text = re.sub(r'<.*?>', '', text)
    # Remove content within curly brackets
    text = re.sub(r'\{.*?\}', '', text)
    # Remove content within parentheses
    text = re.sub(r'\(.*?\)', '', text)
    
    return text


def text_normalize(
    text: str,
    language_code: str,
    lower_case: bool = True,
    remove_numbers: bool = False,
    remove_brackets: bool = False
) -> Optional[str]:
    """
    Apply language-specific text normalization.
    
    Args:
        text: Input text to normalize
        language_code: ISO language code (e.g., 'en', 'fr', 'de')
        lower_case: Whether to convert to lowercase
        remove_numbers: Whether to filter out digit-only text
        remove_brackets: Whether to remove bracketed content
        
    Returns:
        Normalized text, or None if text should be filtered
    """
    if not text or not isinstance(text, str):
        return None
    
    # Normalize unicode
    text = normalize_unicode(text)
    
    # Remove brackets if requested
    if remove_brackets:
        text = remove_brackets_content(text)
    
    # Remove punctuation
    text = remove_punctuation(text, language_code)
    
    # Lowercase if requested
    if lower_case:
        text = text.lower()
    
    # Remove extra whitespace
    text = remove_extra_whitespace(text)
    
    # Filter digit-only text if requested
    if remove_numbers and not remove_digit_only_words(text):
        return None
    
    # Filter empty text
    if not text or text.isspace():
        return None
    
    return text


def batch_normalize_text(
    batch: dict,
    text_column: str = "text",
    language_column: str = "language",
    **normalize_kwargs
) -> dict:
    """
    Apply text normalization to a batch of examples.
    
    Args:
        batch: Dictionary of lists (batch format)
        text_column: Name of the text column
        language_column: Name of the language column
        **normalize_kwargs: Additional arguments for text_normalize
        
    Returns:
        Batch with normalized text
    """
    normalized_texts = []
    
    # If language is same for all samples in batch
    if language_column in batch:
        languages = batch[language_column]
    else:
        # Default to 'en' if no language specified
        languages = ['en'] * len(batch[text_column])
    
    for text, lang in zip(batch[text_column], languages):
        normalized = text_normalize(text, lang, **normalize_kwargs)
        normalized_texts.append(normalized if normalized else "")
    
    batch[text_column] = normalized_texts
    return batch

