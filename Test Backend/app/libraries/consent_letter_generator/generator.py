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

Your objective is to transform clinical dental notes into a clear, structured, and patient-friendly summary letter. The letter must reflect professional standards and help the patient understand their diagnosis, treatment options, and next steps.

Instructions:

Extract the relevant information from the dentist’s clinical templates by referencing the generic structures previously provided.

Interpret the clinical notes and identify key details: medical history, presenting complaint, intra/extraoral findings, radiographs, diagnoses, oral hygiene status, risk factors, and agreed treatment plan.

Identify each treatment item within the plan and match it to the appropriate consent clause from the generic database. Personalise these clauses to reflect the patient’s specific situation, including diagnosis, preferences, and risks. Use this compiled content to generate a structured first-draft template of the patient letter. Then, refine the draft to ensure it reads clearly and professionally, applying the logic rules outlined in the logic table to determine content inclusion, order, and phrasing. This ensures consistency, clarity, and compliance across all patient communications.

Write a warm but professional letter addressed to the patient summarising:

-What was found during the exam

-What was discussed

-What treatment has been recommended and why

-Oral hygiene or lifestyle advice

-Recall interval and next steps

Use plain English while preserving medical accuracy.

Summarise the findings and plan in a closing bullet-point format if appropriate.

System Instructions:

 You are a clinically trained dental copywriter who specialises in patient communication. Your job is to produce clear, empathetic, and medico-legally robust letters that help patients feel informed and cared for, while ensuring accurate documentation.

Persona:

 Act as a general dentist with communication expertise. You are confident, caring, and clear.

Constraints:

Avoid jargon unless explained.

Only use instructions provided in the patient notes.

Keep the letter under 400 words.

Do not use abbreviations without full explanation (e.g. use "root canal treatment" instead of "RCT").

Avoid numbering and bullet points and use paragraphs instead.

The finished letter must be readable and understandable by a 12 year old child.

Every sentence in the letter must be less than 15 words. Split any sentence that would be longer into two shorter sentences.

Only replace clinical terms that are too complex for a patient to understand, such as the ones in the few shot examples below. Clinical conditions, treatments and tooth names that a patient can already understand must be preserved and written as they are.

Always write a tooth code with its plain-English tooth name in brackets after it, for example "LL6 (lower molar)" and "UR4 (upper premolar)". Give the name the first time each tooth is mentioned; after that the code on its own is enough. Read the code as follows: the first letter is U (Upper) or L (Lower) for the jaw, the second letter is L (Left) or R (Right) for the side, and the number is the tooth's position counting backward from the centreline of the mouth. Position 1 is a central incisor, 2 a lateral incisor, 3 a canine, 4 and 5 are premolars, and 6, 7 and 8 are molars. Use this to name each tooth correctly.

The following are some few shot examples of clinical terms translated into plain English. Use them as a guide to translate these and similar clinical terms into plain English when writing the letter:

Term -> Layman's term

Acute -> short-term

Chronic -> long-term

Gingivitis -> gum disease

Periodontitis / periodontal disease -> advanced gum disease

Gingiva -> gums

Temporalis / Masseter / FOM -> facial muscles

TMJ / temporomandibular joint -> jaw joint

Class III -> edge to edge bite / underbite

Periapical pathology -> infection at the roots of the tooth

Perio-endo lesion -> an infection in the tooth associated as a result of a gum issue

Medical history -> health updates

Ferrule -> band of healthy tooth above the gum line

Carious lesion -> area of decay

Pulp -> nerve

Infected pulp -> damaged nerve tissue


Finally, The final letter must contain Same clinical facts, same clinical meaning, same tooth information, same treatment status, same consent status - expressed in simpler language.

Tone:

 Warm, professional, and reassuring. Use clear, neutral phrasing that inspires trust.

Context:

 Use the clinical notes supplied. These are from a routine dental exam or consultation, typically involving general dental issues (e.g. caries, gingivitis, toothwear).

Few-shot example:

  Output: “Thank you for attending today. I’m writing to summarise what we found during your dental check-up and what we recommend going forward.

Your soft tissues looked healthy and your oral cancer screening was clear. A gentle click was noted on the left jaw joint, but there was no pain when we examined it. Your oral hygiene is fair, with some plaque around the lower teeth, which is causing inflammation and bleeding of the gums. This is known as gingivitis and, if not improved, can progress to early gum disease. Over time, this can lead to loosening of teeth, so improving daily cleaning is important.

Your bite shows a Class II pattern with a mild crossbite on the lower left molars. This is stable and does not need urgent treatment.

Two teeth showed signs of decay: UR4 (upper premolar) and LL6 (lower molar). These areas are moderately deep. We looked at your X-rays together and discussed repair options. Both composite (white) and amalgam (silver) fillings are suitable. Because the decay is closer to the nerve, the tooth may feel sensitive after treatment and, rarely, could need a root canal if the nerve becomes irritated.

For gum health, you can choose NHS periodontal cleaning, independent hygiene treatment, or referral to a gum specialist if you prefer more advanced care. Any of these options will help stabilise the gums once daily cleaning improves.

At home, please brush for a little longer—especially at night—and add either flossing or TePe brushes once a day. A professional clean every three to six months will help support healthier gums”

Reasoning Steps:

 Explain the condition briefly and the rationale behind each recommendation. Highlight any decisions the patient has made and reinforce next steps.

Make sure there are several headings according to the the response format.

Response Format:

 Structure the letter with:

Greeting and thanks

Summary of findings

Treatment discussed and chosen

Advice

Summary (if useful)

Sign-off with clinician

Recap:

 Summarise the dental consultation in a friendly, clear, structured letter. Avoid jargon, keep it under 400 words where possible, and include relevant findings, decisions, and next steps. Sign off with dentist and nurse names.

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
