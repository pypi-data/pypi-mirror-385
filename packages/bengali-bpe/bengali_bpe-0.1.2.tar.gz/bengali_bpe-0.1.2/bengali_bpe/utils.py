# bengali_bpe/utils.py

import unicodedata
import re

def normalize_bengali_text(text):
    """
    Normalize Bengali text by:
      - Applying Unicode normalization (NFC)
      - Collapsing multiple whitespace characters into one

    Args:
        text (str): Raw Bengali text.

    Returns:
        str: Normalized text.
    """
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
