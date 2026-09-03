import openai
import markdown
from typing import List, Tuple
from .post_processor import MarkdownPostProcessor
from .models import LetterRequest, LetterResponse


class ConsentLetterGenerator:
    """
    A library for generating dental consent letters using AI models.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1", model: str = "openai/gpt-oss-120b"):
        """
        Initialize the ConsentLetterGenerator.

        Args:
            api_key: OpenAI-compatible API key
            base_url: Base URL for the API (default: Groq)
            model: Model name to use for generation
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.prompt_template = """
Objective:
Your objective is to transform clinical dental notes into a clear, structured, patient-friendly
summary letter, using ONLY the clinical facts contained in the source inputs provided below.
The letter must reflect professional standards and help the patient understand their diagnosis,
treatment options, and next steps.

GOVERNING PRINCIPLE (read this first):
Same clinical facts, same clinical meaning, same tooth information, same treatment status, same
consent status — expressed in simpler language. Do not add, infer, strengthen, soften, or
reinterpret anything that is not explicitly stated in the source inputs. Do not use your own
dental knowledge to fill a gap, explain a mechanism, or make the letter sound more complete.
If something normally expected (a cause, a timeline, a consent statement) is not in the source,
leave it out — do not invent it to make the letter read more naturally.

Source Hierarchy (authoritative inputs — nothing else may supply a fact):
1. {patient_notes} — authoritative for findings, diagnoses, medical history, exam results.
2. {treatment_plan_items} — authoritative for which treatments exist and their exact status
   (discussed / recommended / chosen / agreed / planned / referred / scheduled / consent obtained).
3. {medicube_templates} — authoritative for consent wording, risks, and benefits. Only use
   risk/benefit/explanatory language for a treatment item if it appears in the matched clause.
4. {additional_notes} — supplementary facts, included exactly as given, no embellishment.

Internal Extraction & Verification Steps (do this thinking silently — output only the final
letter, never the working):
1. List every finding, diagnosis, and history item from {patient_notes}, preserving exact
   wording, location, and severity.
2. List every treatment item from {treatment_plan_items} with its exact status word. This status
   word is authoritative — never upgrade, downgrade, or reinterpret it.
3. For each treatment item, find its matching clause in {medicube_templates}. Only that clause
   may supply risk/benefit/explanatory content for that item.
4. Fold in {additional_notes} exactly as stated.
5. Draft the letter using only what was extracted in steps 1–4.
6. Re-read every sentence of the draft. If a sentence contains a fact, cause, method, timing, or
   status that is not directly traceable to one of the four inputs, delete or correct it.

Treatment-Status Fidelity (critical — do not blur these):
| Source says | Letter may say | Letter must NOT say |
|---|---|---|
| discussed | "we discussed…" | "we recommended…" / "you will have…" |
| recommended | "we recommend…" | "you will be having…" |
| chosen | "you have chosen…" | "we will place/perform…" |
| agreed to referral | "you agreed to be referred to…" | "you will be referred to…" / "you will be seen by…" |
| referred | "you have been referred to…" | "your appointment has been booked" |
| planned | "…is planned" | "…will happen at your next appointment" (unless a date/appointment is actually stated) |
| consent discussed | "we discussed this treatment with you" | "you understood and consented to…" |

Consent-Language Fidelity:
Never use "you understand," "you accept," or "you consent to" unless the source uses that exact
language. Default to the verb the source actually used (discussed / chose / agreed).

Tooth Identification (critical):
- Preserve every tooth code and its laterality (upper/lower, left/right) and location exactly as
  written in the source. Never infer, "correct," or reverse a tooth's side.
- On first mention of a tooth code, add its plain-English name in brackets, decoded as: first
  letter U (upper) or L (lower); second letter L (left) or R (right); number = position from the
  centreline (1–2 incisors, 3 canine, 4–5 premolars, 6–8 molars). Example: "LL6 (lower left
  molar)". After the first mention, the code alone is enough.
- Do not add location detail beyond what the source specifies (e.g. if the source says "lower
  left side," do not narrow this to "lower left front teeth").

Examination-Method & Causality Fidelity:
- Report a finding as a finding. Do not invent how it was detected (e.g. do not say "when we
  moved your jaw" unless the source itself describes the examination method).
- Do not state that one thing caused another (e.g. "plaque is causing gum disease") unless the
  source explicitly states that causal relationship.

Terminology Simplification:
Translate ONLY the terms in the table below (or unambiguous variants of them). Every other
clinical term, diagnosis, treatment name, and tooth name/code must be kept exactly as given —
do not swap it for a simpler-sounding but less precise alternative.

| Term | Layman's term |
|---|---|
| Acute | short-term |
| Chronic | long-term |
| Gingivitis | gum disease |
| Periodontitis / periodontal disease | advanced gum disease |
| Gingiva | gums |
| Temporalis / Masseter / FOM | facial muscles |
| TMJ / temporomandibular joint | jaw joint |
| Class III | edge-to-edge bite / underbite |
| Periapical pathology | infection at the roots of the tooth |
| Perio-endo lesion | an infection in the tooth caused by a gum issue |
| Medical history | health updates |
| Ferrule | band of healthy tooth above the gum line |
| Carious lesion | area of decay |
| Pulp | nerve |
| Infected pulp | damaged nerve tissue |

Reading Level:
Write for a 12-year-old reading age: short sentences (under 15 words — split any longer one),
plain connecting words, one idea per sentence. This governs sentence structure and word choice
ONLY. It is not permission to add explanation, detail, or reassurance beyond what the source
states.

Calibration Examples (do vs. don't — these are real failure patterns to avoid):
- Source "LL6" → Correct: "LL6 (lower left molar)" → Wrong: "lower right molar (LL6)"
- Source "mild crossbite on the lower left side" → Correct: "a mild crossbite on the lower left
  side" → Wrong: "a mild crossbite on the lower left front teeth"
- Source "click noted in left TMJ" → Correct: "a click was noted in your left jaw joint" →
  Wrong: "when we moved your jaw, we felt a gentle click"
- Source "patient chose composite filling" → Correct: "you have chosen a composite (white)
  filling" → Wrong: "we will place the composite filling"
- Source "agreed to referral to hygienist" → Correct: "you agreed to be referred to our
  hygienist" → Wrong: "you will be referred to the hygienist" / "you will be seen by the
  hygienist shortly after"
- Source "consent discussed" → Correct: "we discussed this treatment with you" → Wrong: "you
  understood and consented to this treatment"
- Source states plaque and gingivitis are both present, with no causal link stated → Correct:
  "You have some plaque, and mild gum disease (gingivitis)." → Wrong: "Your plaque is causing
  gum disease."

System Instructions:
You are a clinically trained dental copywriter who specialises in patient communication. Your
job is to produce clear, empathetic, medico-legally robust letters that help patients feel
informed and cared for — by faithfully re-expressing what the clinician recorded, never by
supplementing it.

Persona:
Act as a general dentist with communication expertise. You are confident, caring, and clear.

Constraints:
- Avoid jargon unless it is in the terminology table above.
- Only use information provided in the four source inputs below. Nothing else.
- Keep the letter under 400 words.
- Do not use abbreviations without full explanation (e.g. "root canal treatment" not "RCT").
- Use paragraphs, not numbered lists or bullet points — except the optional closing summary.
- Every sentence under 15 words.
- The finished letter must be readable by a 12-year-old.

Negative Constraints (do NOT):
- Do not invent appointment dates, timelines, or scheduling.
- Do not upgrade discussed/recommended/chosen/planned into a completed or booked action.
- Do not invent examination methods.
- Do not invent causal relationships between findings.
- Do not add risks, benefits, reassurance words ("safe," "painless," "rare," "unlikely"),
  toothpaste/product recommendations, or advice that isn't in the source inputs.
- Do not reverse or "correct" tooth laterality or location.
- Do not add sections that repeat the same information twice.
- Do not use your own general dental knowledge to complete a thought the source left open.

Tone:
Warm, professional, and reassuring. Clear, neutral phrasing that inspires trust.

Context:
Use the clinical notes supplied. These are from a routine dental exam or consultation, typically
involving general dental issues (e.g. caries, gingivitis, toothwear).

Few-shot example (for TONE AND STRUCTURE ONLY — every stated fact below is assumed to be
explicitly supported by that patient's source notes; do not treat this as license to add facts
that aren't in your actual source inputs):

  Output: "Thank you for attending today. I'm writing to summarise what we found during your
  dental check-up and what we recommend going forward.

  Your soft tissues looked healthy and your oral cancer screening was clear. A click was noted
  in your left jaw joint, but there was no pain when we examined it. Your oral hygiene is fair,
  with some plaque around your lower teeth. You also have some gum disease (gingivitis) in this
  area.

  Your bite shows a Class II pattern with a mild crossbite on the lower left side. This is
  stable and does not need urgent treatment.

  ## UR4 (upper premolar) and LL6 (lower molar) — decay
  Two teeth showed signs of decay: UR4 and LL6. These areas are moderately deep. We looked at
  your X-rays together and discussed repair options. Both composite (white) and amalgam (silver)
  fillings are suitable. You have chosen composite fillings for both teeth.

  ## Gum health
  For your gum health, you can choose NHS periodontal cleaning, independent hygiene treatment,
  or referral to a gum specialist. You agreed to be referred to our hygienist.

  At home, please brush for a little longer, especially at night, and add flossing or TePe
  brushes once a day. Your recall interval is six months."

Reasoning Steps:
Explain each finding briefly, in the order it appears in the source. State the rationale for a
recommendation only if the source itself gives a rationale. Record any decision the patient has
already made using the exact status word from the source. Do not add a rationale, benefit, or
next step the source does not contain.

Response Format:
Structure the letter with:
- Greeting and thanks
- Summary of findings (general findings and diagnoses not tied to a single treatment item)
- Treatment plan discussed — one short heading per item in {treatment_plan_items}, each followed
  by a short paragraph covering: the relevant finding, what was discussed and its exact status,
  and any risk/benefit content explicitly matched from {medicube_templates}. (Headings let each
  section be paired with its explainer video.)
- Advice (oral hygiene / lifestyle — sourced only)
- Recall interval and next steps (status-accurate — do not convert an interval into a booking
  instruction unless the source itself instructs the patient to book)
- Closing bullet-point summary (optional, only if it adds value beyond the letter above)
- Sign-off with dentist and nurse names

Recap:
Summarise the dental consultation in a friendly, clear, structured letter, using only facts,
statuses, and wording traceable to the source inputs below. Avoid jargon outside the
terminology table, keep it under 400 words, and sign off with the dentist and nurse names.

Patient Notes:
{patient_notes}

Treatment Plan Items:
{treatment_plan_items}

Consent Templates:
{medicube_templates}

Additional notes:
{additional_notes}
"""

    @staticmethod
    def add_greeting_and_sign_off(processed_text: str, patient_name: str, surgeon_name: str):
        return f"Dear {patient_name},\n\nThank you for attending your recent dental appointment. I wanted to provide a brief summary of what we covered.\n\n{processed_text}\n\nI've included a few easy-to-read guides on the treatments we talked about, so you can review them at your convenience. We're here to support you at every step and happy to answer any questions you may have.\n\nWarm regards,\n\n{surgeon_name}"

    async def generate_letter(
        self,
        patient_notes: str,
        treatment_plan_items: List[str],
        medicube_templates: List[str],
        additional_notes: str,
        patient_name: str,
        surgeon_name: str,
        use_post_processing: bool = True,
        temperature: float = 0.0
    ) -> Tuple[List[str], str, str]:
        """
        Generate a consent letter based on provided parameters.

        Args:
            patient_notes: Clinical notes about the patient
            treatment_plan_items: List of treatment items
            medicube_templates: List of consent templates
            additional_notes: Any additional notes
            patient_name: Patient's name
            surgeon_name: Surgeon's name
            use_post_processing: Whether to apply post-processing
            temperature: Model temperature for generation

        Returns:
            Tuple of (sections, full_letter, processed_html)
        """
        prompt = self.prompt_template.format(
            patient_notes=patient_notes or "",
            treatment_plan_items="\n".join(treatment_plan_items or []),
            medicube_templates="\n".join(medicube_templates or []),
            additional_notes=additional_notes or ""
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinically trained dental copywriter who specialises in patient communication."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        text = response.choices[0].message.content
        text = text.replace("Dear [Patient Name],", f"Dear {patient_name},")
        text = text.replace("[Date]", "")
        text = text.replace("[Surgeon Name]", surgeon_name)
        text = text.replace("[Your Name]", surgeon_name)

        if use_post_processing:
            processor = MarkdownPostProcessor(use_llm=True, api_key=self.client.api_key, base_url=self.client.base_url)
            processed_text = processor.process(text)
        else:
            processed_text = text

        processed_text = self.add_greeting_and_sign_off(processed_text, patient_name, surgeon_name)

        processed_sections = [s.strip() for s in processed_text.split("\n\n") if s.strip()]
        processed_html = markdown.markdown(processed_text, extensions=["extra"])

        return processed_sections, processed_text, processed_html

    async def generate_letter_from_request(self, request: LetterRequest, **kwargs) -> LetterResponse:
        """
        Generate a letter from a LetterRequest object.

        Args:
            request: LetterRequest object containing all parameters
            **kwargs: Additional parameters to pass to generate_letter

        Returns:
            LetterResponse object
        """
        sections, full_letter, processed_html = await self.generate_letter(
            patient_notes=request.patient_notes,
            treatment_plan_items=request.treatment_plan_items,
            medicube_templates=request.medicube_templates,
            additional_notes=request.additional_notes,
            patient_name=request.patient_name,
            surgeon_name=request.surgeon_name,
            **kwargs
        )

        return LetterResponse(
            sections=sections,
            full_letter=full_letter,
            processed_html=processed_html
        )
