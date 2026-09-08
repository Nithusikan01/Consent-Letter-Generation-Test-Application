import os
import unicodedata

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from libraries.consent_letter_generator import (
    ConsentLetterGenerator,
    LetterRequest,
    LETTER_STYLES,
    DEFAULT_LETTER_STYLE,
)
from utils import _remove_invalid_placeholders, _normalize_unicode_chars

router = APIRouter()

API_KEY = os.getenv("OPENAPI_API_KEY", os.getenv("openapi_api_key", ""))

NARRATIVE_LETTER_STYLE = "narrative"


class TestLetterRequest(BaseModel):
    patient_name: str
    clinician_name: str
    patient_notes: str


class TestLetterResponse(BaseModel):
    html: str
    full_letter: str
    style: str


class LetterStyle(BaseModel):
    id: str
    label: str
    description: str
    endpoint: str


STYLE_ENDPOINTS = {
    DEFAULT_LETTER_STYLE: "/test/generate-patient-letter",
    NARRATIVE_LETTER_STYLE: "/test/generate-patient-letter-narrative",
}


async def _generate(req: TestLetterRequest, style: str) -> TestLetterResponse:
    """Shared generation path — the two endpoints differ only by letter style."""
    if not req.patient_notes or not req.patient_notes.strip():
        raise HTTPException(status_code=400, detail="patient_notes must not be empty")

    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENAPI_API_KEY is not set in the environment")

    try:
        generator = ConsentLetterGenerator(api_key=API_KEY)
        letter_request = LetterRequest(
            patient_notes=req.patient_notes,
            treatment_plan_items=[],
            medicube_templates=[],
            additional_notes="",
            patient_name=req.patient_name or "Unknown",
            surgeon_name=req.clinician_name or "Unknown",
        )
        letter_response = await generator.generate_letter_from_request(
            request=letter_request,
            use_post_processing=True,
            temperature=0.05,
            style=style,
        )

        html = letter_response.processed_html.replace("\n", "")
        html = _normalize_unicode_chars(html)
        html = _remove_invalid_placeholders(html)
        html = unicodedata.normalize("NFKC", html)

        return TestLetterResponse(html=html, full_letter=letter_response.full_letter, style=style)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating consent letter: {e}")


@router.get("/letter-styles", response_model=List[LetterStyle])
async def list_letter_styles() -> List[LetterStyle]:
    """The letter styles the UI can offer, and the endpoint that produces each."""
    return [
        LetterStyle(
            id=style_id,
            label=cfg["label"],
            description=cfg["description"],
            endpoint=STYLE_ENDPOINTS[style_id],
        )
        for style_id, cfg in LETTER_STYLES.items()
        if style_id in STYLE_ENDPOINTS
    ]


@router.post("/generate-patient-letter", response_model=TestLetterResponse)
async def generate_patient_letter_test(req: TestLetterRequest) -> TestLetterResponse:
    """Bulleted letter — findings and options broken into short bullet points.

    Mirrors the logic in api_v2.consent_bundle.generate_patient_letter, which only
    receives patient_notes (treatment items are looked up from the ConsentBundle in
    the real app, never sent separately). This test endpoint takes patient/clinician
    names directly in the request instead of looking them up, and returns the
    generated HTML instead of saving it.
    """
    return await _generate(req, DEFAULT_LETTER_STYLE)


@router.post("/generate-patient-letter-narrative", response_model=TestLetterResponse)
async def generate_patient_letter_narrative(req: TestLetterRequest) -> TestLetterResponse:
    """Narrative letter — the same content written as flowing paragraphs.

    Identical to /generate-patient-letter in every clinical respect: same notes in,
    same sections, same grounding rules. Only the presentation differs, so the two
    can be compared side by side to decide which reads better for patients.
    """
    return await _generate(req, NARRATIVE_LETTER_STYLE)
