import os
import unicodedata

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from libraries.consent_letter_generator import ConsentLetterGenerator, LetterRequest
from utils import _remove_invalid_placeholders, _normalize_unicode_chars

router = APIRouter()

API_KEY = os.getenv("OPENAPI_API_KEY", os.getenv("openapi_api_key", ""))


class TestLetterRequest(BaseModel):
    patient_name: str
    clinician_name: str
    treatment_plan_items: List[str] = []
    patient_notes: str


class TestLetterResponse(BaseModel):
    html: str
    full_letter: str


@router.post("/generate-patient-letter", response_model=TestLetterResponse)
async def generate_patient_letter_test(req: TestLetterRequest) -> TestLetterResponse:
    """Standalone patient-letter generation for the evaluation UI.

    Mirrors the logic in api_v2.consent_bundle.generate_patient_letter but takes
    patient/clinician/treatment details directly in the request instead of looking
    them up from a ConsentBundle, and returns the generated HTML instead of saving it.
    """
    if not req.patient_notes or not req.patient_notes.strip():
        raise HTTPException(status_code=400, detail="patient_notes must not be empty")

    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENAPI_API_KEY is not set in the environment")

    try:
        generator = ConsentLetterGenerator(api_key=API_KEY)
        letter_request = LetterRequest(
            patient_notes=req.patient_notes,
            treatment_plan_items=req.treatment_plan_items,
            medicube_templates=[],
            additional_notes="",
            patient_name=req.patient_name or "Unknown",
            surgeon_name=req.clinician_name or "Unknown",
        )
        letter_response = await generator.generate_letter_from_request(
            request=letter_request,
            use_post_processing=True,
            temperature=0.05,
        )

        html = letter_response.processed_html.replace("\n", "")
        html = _normalize_unicode_chars(html)
        html = _remove_invalid_placeholders(html)
        html = unicodedata.normalize("NFKC", html)

        return TestLetterResponse(html=html, full_letter=letter_response.full_letter)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating consent letter: {e}")
