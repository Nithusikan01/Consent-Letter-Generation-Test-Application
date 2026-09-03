from pydantic import BaseModel
from typing import List, Optional

class LetterRequest(BaseModel):
    patient_notes: Optional[str] = None
    treatment_plan_items: Optional[List[str]] = None
    medicube_templates: Optional[List[str]] = None
    additional_notes: Optional[str] = None
    patient_name: Optional[str] = None
    surgeon_name: Optional[str] = None

class LetterResponse(BaseModel):
    sections: List[str]
    full_letter: str
    processed_html: str
