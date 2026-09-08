"""
Consent Letter Generator Library

A Python library for generating dental consent letters using AI models.
"""

from .generator import ConsentLetterGenerator, LETTER_STYLES, DEFAULT_LETTER_STYLE
from .models import LetterRequest, LetterResponse

__version__ = "0.1.0"
__all__ = [
    "ConsentLetterGenerator",
    "LetterRequest",
    "LetterResponse",
    "LETTER_STYLES",
    "DEFAULT_LETTER_STYLE",
]
