import asyncio
import os
import re
import unicodedata

import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from libraries.consent_letter_generator import ConsentLetterGenerator, LetterRequest
from utils import _remove_invalid_placeholders, _normalize_unicode_chars

router = APIRouter()

API_KEY = os.getenv("OPENAPI_API_KEY", os.getenv("openapi_api_key", ""))

# Groq's free tier allows 8,000 tokens per minute, and one letter costs roughly
# 7,500. A second attempt inside the same minute therefore always fails, so a
# short wait is worth taking automatically; anything longer is handed back to
# the caller with the wait time rather than retried silently.
AUTO_RETRY_MAX_WAIT_SECONDS = 30


def _retry_after_seconds(message: str) -> float | None:
    """Groq reports 'Please try again in 1m46.704s' / 'in 8.5s' in the 429 body."""
    match = re.search(r'try again in\s*(?:(\d+)m)?\s*([\d.]+)s', message, re.I)
    if not match:
        return None
    minutes = int(match.group(1)) if match.group(1) else 0
    return minutes * 60 + float(match.group(2))


class TestLetterRequest(BaseModel):
    patient_name: str
    clinician_name: str
    patient_notes: str


class TestLetterResponse(BaseModel):
    html: str
    full_letter: str


@router.post("/generate-patient-letter", response_model=TestLetterResponse)
async def generate_patient_letter_test(req: TestLetterRequest) -> TestLetterResponse:
    """Standalone patient-letter generation for the evaluation UI.

    Prose throughout, with bullet points used only where multiple treatment options
    need to be compared. Bulleted letters are harder for patients to read, so bullets
    are confined to the options section.

    Mirrors the logic in api_v2.consent_bundle.generate_patient_letter, which only
    receives patient_notes (treatment items are looked up from the ConsentBundle in
    the real app, never sent separately). This test endpoint takes patient/clinician
    names directly in the request instead of looking them up, and returns the
    generated HTML instead of saving it.
    """
    if not req.patient_notes or not req.patient_notes.strip():
        raise HTTPException(status_code=400, detail="patient_notes must not be empty")

    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENAPI_API_KEY is not set in the environment")

    generator = ConsentLetterGenerator(api_key=API_KEY)
    letter_request = LetterRequest(
        patient_notes=req.patient_notes,
        treatment_plan_items=[],
        medicube_templates=[],
        additional_notes="",
        patient_name=req.patient_name or "Unknown",
        surgeon_name=req.clinician_name or "Unknown",
    )

    try:
        try:
            letter_response = await generator.generate_letter_from_request(
                request=letter_request,
                use_post_processing=True,
                temperature=0.05,
            )
        except openai.RateLimitError as rate_error:
            wait = _retry_after_seconds(str(rate_error))

            # A short wait is almost always the per-minute budget refilling, so
            # take it once rather than making the user retry by hand.
            if wait is not None and wait <= AUTO_RETRY_MAX_WAIT_SECONDS:
                await asyncio.sleep(wait + 1)
                letter_response = await generator.generate_letter_from_request(
                    request=letter_request,
                    use_post_processing=True,
                    temperature=0.05,
                )
            else:
                if wait is None:
                    detail = "The AI service rate limit has been reached. Please try again shortly."
                elif wait >= 120:
                    detail = (
                        f"The AI service rate limit has been reached. Please try again in about "
                        f"{round(wait / 60)} minutes. If this keeps happening the daily quota is "
                        f"likely exhausted."
                    )
                else:
                    detail = (
                        f"The AI service rate limit has been reached. Please try again in "
                        f"{round(wait)} seconds."
                    )
                # 429 rather than 500: this is a quota condition, not a failure
                # of the request, and the UI can say so plainly.
                raise HTTPException(status_code=429, detail=detail)

        html = letter_response.processed_html.replace("\n", "")
        html = _normalize_unicode_chars(html)
        html = _remove_invalid_placeholders(html)
        html = unicodedata.normalize("NFKC", html)

        return TestLetterResponse(html=html, full_letter=letter_response.full_letter)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating consent letter: {e}")
