# smart_slugify/slugify.py

import unicodedata
import re
from typing import Optional

DEFAULT_SEPARATOR = "-"

def slugify(
    text: str,
    lowercase: bool = True,
    separator: str = DEFAULT_SEPARATOR,
    max_length: Optional[int] = None,
) -> str:
    """
    Convert the input `text` into a slug:
    - Normalize and strip accents
    - Lowercase (if lowercase=True)
    - Replace invalid characters with separator
    - Collapse multiple separators
    - Trim leading/trailing separators
    - Optionally truncate to max_length (naively)
    """

    if text is None:
        return ""

    # 1. Normalize Unicode to NFKD and remove diacritics
    normalized = unicodedata.normalize("NFKD", text)
    # Build a string, discarding combining characters / diacritics
    no_accents = "".join(
        ch for ch in normalized
        if not unicodedata.combining(ch)
    )

    # 2. Lowercase if needed
    if lowercase:
        no_accents = no_accents.lower()

    # 3. Replace invalid characters (anything not alphanumeric) with separator
    # We'll allow alphanumeric and treat others as boundaries.
    # But first, define a pattern to match valid characters:
    # Note: \w includes underscore; we may want only [a-z0-9], but for now include underscores.
    # We'll treat anything not alnum as separator.
    # Use a regex to replace runs of invalid chars with a single separator:
    invalid_pattern = r"[^0-9a-zA-Z]+"
    slug = re.sub(invalid_pattern, separator, no_accents)

    # 4. Collapse repeated separators (e.g. "--" or "- -") into single
    repeated_sep_pattern = re.escape(separator) + r"{2,}"
    slug = re.sub(repeated_sep_pattern, separator, slug)

    # 5. Trim leading/trailing separators
    slug = slug.strip(separator)

    # 6. Truncate if max_length is given
    if max_length is not None and max_length > 0 and len(slug) > max_length:
        slug = slug[:max_length]
        # After truncation, strip trailing separator again
        slug = slug.rstrip(separator)

    return slug