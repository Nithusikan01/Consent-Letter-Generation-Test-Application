import re


def _remove_invalid_placeholders(body: str) -> str:
    valid_placeholders = ["signature(Mandatory)", "signature(Optional)", "signature_mandatory", "signature_optional", "clinician_signature", "patient_name", "patient_dob", "patient_address", "consent_bundle_created_date", "clinician_name", "practice_name"]

    pattern = r"\[(.*?)\]"
    matches = re.findall(pattern, body)

    for match in matches:
        if match not in valid_placeholders:
            body = body.replace(f"[{match}]", "")

    return body

def _normalize_unicode_chars(text):
    """Replace problematic Unicode characters with ASCII equivalents"""
    
    # Dictionary of problematic Unicode characters and their ASCII replacements
    char_replacements = {
        '\u2011': '-',  # Non-breaking hyphen → ASCII hyphen
        '\u2012': '-',  # Figure dash → ASCII hyphen
        '\u2013': '-',  # En dash → ASCII hyphen
        '\u2014': '-',  # Em dash → ASCII hyphen
        '\u2015': '-',  # Horizontal bar → ASCII hyphen
        '\u2018': "'",  # Left single quotation mark → ASCII apostrophe
        '\u2019': "'",  # Right single quotation mark → ASCII apostrophe
        '\u201C': '"',  # Left double quotation mark → ASCII quote
        '\u201D': '"',  # Right double quotation mark → ASCII quote
        '\u2026': '...',  # Horizontal ellipsis → ASCII dots
        '\u00A0': ' ',  # Non-breaking space → ASCII space
        '\u2002': ' ',  # En space → ASCII space
        '\u2003': ' ',  # Em space → ASCII space
        '\u2009': ' ',  # Thin space → ASCII space
        '\u200B': '',   # Zero-width space → remove
        '\u00AD': '',   # Soft hyphen → remove        
        
        # added on 12/08/2026 as per the issue raised
        # Additional common Unicode characters seen in Word, Outlook, PDFs and copy/paste content
        '\u2010': '-',  # Hyphen
        '\u2212': '-',  # Minus sign

        # Additional quote variants
        '\u201A': "'",  # Single low-9 quotation mark
        '\u201B': "'",  # Single high-reversed-9 quotation mark
        '\u201E': '"',  # Double low-9 quotation mark
        '\u201F': '"',  # Double high-reversed-9 quotation mark

        # Additional spacing characters
        '\u202F': ' ',  # Narrow no-break space

        # Additional invisible/zero-width characters
        '\u200C': '',   # Zero-width non-joiner
        '\u200D': '',   # Zero-width joiner
        '\u2060': '',   # Word joiner
        '\uFEFF': '',   # BOM / zero-width no-break space
    }
    
    for unicode_char, ascii_replacement in char_replacements.items():
        text = text.replace(unicode_char, ascii_replacement)
    
    return text
