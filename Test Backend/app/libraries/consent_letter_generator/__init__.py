"""
Consent Letter Generator Library

A Python library for generating dental consent letters using AI models.
"""

from .generator import ConsentLetterGenerator
from .models import LetterRequest, LetterResponse

__version__ = "0.1.0"
__all__ = ["ConsentLetterGenerator", "LetterRequest", "LetterResponse"]
