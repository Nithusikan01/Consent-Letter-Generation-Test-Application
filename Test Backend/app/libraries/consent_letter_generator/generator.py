import re
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
You are drafting a patient letter that summarizes a dental consultation and its recommended treatment, for a patient with no medical background (target reading age: 12).

═══════════════════════════════════════
GROUNDING RULE — THIS OVERRIDES EVERYTHING ELSE BELOW
═══════════════════════════════════════
Every clinical fact, price, explanation, cause, risk, or recommendation you write MUST come directly from the Patient Notes, Treatment Plan Items, Consent Templates, or Additional Notes provided below.
- Do NOT use your own dental/medical knowledge to explain a condition, guess a cause, predict a prognosis, or fill a gap in the notes.
- If a patient would reasonably want to know something and it is not stated in the source material, leave it out entirely. Do not infer it, generalize from typical cases, or reason it out from general dental knowledge.
- If you are even slightly unsure whether a fact came from the source material, do not include it.

A RISK IS NOT A FINDING:
A risk rating describes what MIGHT happen in future. It is never evidence that the problem is present now, and it never attaches to a particular tooth.
- "Caries risk: high" means this patient is at high risk of developing decay in future. It does NOT mean any tooth currently has decay, a cavity, or a carious lesion. Never write that a specific tooth "has decay", "shows a small area of decay", or similar unless the notes state decay on that tooth.
- The same applies to perio risk, toothwear risk, and any other risk rating.
- Report a risk rating as a risk ("your risk of future decay was assessed as high"), never as a diagnosis.

USE THE REASON THE NOTES GIVE:
Where the notes state WHY a treatment is being done, that stated reason is the only reason you may give.
- Example: if the notes say the teeth are short and so fillings will be added, the reason is that the teeth are short — to build them up. Do NOT substitute a more typical-sounding reason such as decay, damage, or infection.
- If the notes give no reason for a treatment, describe the treatment without a reason. An unexplained treatment is acceptable; an invented explanation is not.

═══════════════════════════════════════
STEP 1 — EXTRACT (internal only — do not show this in your output)
═══════════════════════════════════════
Before writing anything, list for yourself only the facts explicitly present in the input below:
- Findings (exam, radiographs, intra/extraoral) — what is actually present NOW
- Risk ratings (caries risk, perio risk, toothwear risk, etc.) — list these SEPARATELY from findings; they are about future risk, not present disease
- Diagnoses explicitly stated
- Every distinct treatment OPTION discussed, each matched to its consent clause from the Consent Templates
- For each treatment, the REASON the notes give for it, in the notes' own terms (e.g. "the teeth are short"). If the notes give no reason, record "no reason stated" — do not supply one.
- For each MATERIAL or treatment type, every property the notes state about it — how long it lasts, whether it needs tooth preparation, appearance, durability. These are frequently given ONCE, in a comparison sentence well away from the numbered options (e.g. "composite veneer (lasts 3-8 years) vs an emax veneer (lasts 15 years but needs some tooth prep)"). Record each property against its material so it can be carried into every option that uses that material.
- Every price, fee, or cost figure stated for a treatment or option — copy the exact figure and currency symbol (e.g. "£1,106"). Never round, estimate, average, or omit a stated figure.
- Advice or instructions explicitly given
- Recall interval, if stated
Anything not explicitly present does not make this list — and therefore does not make the letter.

TOOTH-BY-TOOTH MAPPING (do this as part of Step 1, and get it right — errors here reach the patient):
Notes often state which treatment goes on which tooth in ONE detailed sentence, and then repeat a FLAT LIST of every tooth involved when summarising an option. These are not the same thing.
- Build an explicit map of tooth code → treatment, taken from the DETAILED sentence that names the treatment ("fillings added to the UL1 and LL1", "a veneer placed on the UR1 and LR1").
- A flat list of teeth in an option summary (e.g. "composite veneers / filling mix on the UR2, UR1, UL1, LR1 and LL1 teeth") lists every tooth INVOLVED in that option. It does NOT mean every tooth in it gets the same treatment. Never read such a list as if it were the veneer list or the filling list — resolve each tooth against the detailed sentence instead.
- A tooth gets exactly ONE treatment unless the notes explicitly say otherwise. The same tooth code must never end up under two different treatments.
- If the notes genuinely do not say which treatment a listed tooth gets, describe the option without assigning that tooth to a specific treatment. Do not guess, and do not split the list evenly.

═══════════════════════════════════════
STEP 2 — DECIDE THE STRUCTURE
═══════════════════════════════════════
Look at what you extracted in Step 1:
- If the notes describe TWO OR MORE distinct treatment options that the patient is choosing between (e.g. "option 1 / option 2", "or", a numbered list of alternatives), each option MUST get its own subsection in the "Treatment options" part of the letter — see the formatting rules and worked example below.
- If there is only one treatment path, describe it in a single "Treatment recommended" section, in plain prose, with no sub-headings.

═══════════════════════════════════════
STEP 3 — WRITE THE LETTER
═══════════════════════════════════════
Using ONLY the facts from Step 1, write the BODY of a letter with these sections, in this order:
1. What we found, in plain English (prose, no headings/bullets)
2. Treatment options we discussed and why — tie each recommendation back to a finding, using only the reasoning present in the source, never your own
3. Home care / lifestyle advice — only if explicitly stated in the source (prose)
4. Next steps and recall interval — only if explicitly stated in the source (prose)

DO NOT write a salutation, greeting, opening thank-you, or sign-off. Specifically, do not begin with "Dear ...", "Thank you for attending/coming in ...", or any similar opening line, and do not end with "Warm regards", "Kind regards", "Yours sincerely", or the clinician's name. The greeting and sign-off are added automatically after you finish — anything you write of that kind is duplicated in the final letter. Start directly with what was found.

FORMATTING RULES FOR SECTION 2 (Treatment options):
- If Step 2 found multiple options: give each option its own short heading in the form "### Option 1: <short name>" (numbered in the order the source presents them), followed by 1-3 plain-English sentences describing what it involves, then a line stating its cost exactly as given, e.g. "Estimated cost: £1,106."
- CARRY MATERIAL PROPERTIES INTO EVERY OPTION THAT USES THAT MATERIAL. If Step 1 recorded a property for a material — how long it lasts, whether it needs tooth preparation, its appearance or durability — it MUST appear in each option using that material, even though the notes state it only once and somewhere else entirely (typically in the discussion, not in the numbered option). The patient is choosing between these options largely on how long each lasts, so a stated lifespan is never optional. If the notes give a lifespan for one material, the option using the other material must carry its stated lifespan too — never state one and omit the other.
- These properties may be written as a short bullet list under the option or folded into its sentences, whichever reads better. Include only properties the source actually states — never invent generic pros/cons.
- If there is only one option: describe it in prose. Still state its cost exactly as given if the source contains one. Do not add sub-headings for a single option.
- Every cost/fee figure present in the source MUST appear next to its matching option — never drop pricing that was explicitly given, even if it feels repetitive.

WORKED EXAMPLE (formatting and tooth-mapping only — these clinical facts are illustrative and must NEVER appear in a real letter; the teeth and figures below are deliberately different from any real case):

Patient notes: "crowns needed on the LR5 and LL5, and a filling on the UR6. In order to match the LR5 I would also do the LR4 crown. pt unsure which to go for - can do either options: 1) crown / filling mix on the LR4, LR5, LL5 and UR6 teeth, total cost £820  2) crowns on all four teeth, £2400, longer lasting"

Step 1 tooth map, taken from the DETAILED sentence (not the flat list):
- crown → LR5, LL5, LR4
- filling → UR6
The flat list in option 1 ("LR4, LR5, LL5 and UR6") is only the set of teeth INVOLVED. UR6 stays a filling there. In option 2 the source explicitly says crowns on all four, so UR6 becomes a crown in that option only.

WRONG (never do this — UR6 is double-booked as both a crown and a filling):

### Option 1: Crowns and a filling
This involves crowns on the LR4, LR5, LL5 and UR6, and a filling on the UR6. Estimated cost: £820.

CORRECT:

We discussed two ways to address this:

### Option 1: Crowns and a filling
This involves crowns on the LR4, LR5 and LL5, and a filling on the UR6. Estimated cost: £820.

### Option 2: Crowns on all four teeth
This involves crowns on the LR4, LR5, LL5 and UR6, and offers a longer-lasting result. Estimated cost: £2,400.

You have not yet decided which option to go for.

GENERAL WRITING RULES:
- Write for a reader with no medical background — aim for a reading level a 12-year-old could follow comfortably.
- The first time any clinical term appears, explain it immediately in plain words, e.g. "gum disease (gingivitis)." Use the glossary below where it applies. Never use an abbreviation without spelling it out in full at first use.
- Do not replace a specific tooth code (e.g. "UR1"), treatment name (e.g. "composite veneer," "root canal treatment"), or diagnosis with a vague substitute — only simplify genuine jargon, not clinical specifics.
- Use short sentences and short paragraphs outside of the Treatment options section.
- Keep the full letter under {word_limit} words.
- Tone: warm, professional, reassuring — never alarming, never clinical or cold.

GLOSSARY — use only where it improves understanding without changing clinical meaning; if a term isn't listed, or its layman's-term column below is blank, leave it as written rather than inventing a simplification:
- Acute → short-term
- Chronic → long-term
- Gingivitis → gum disease
- Periodontitis / periodontal disease → advanced gum disease
- Gingiva → gums
- Temporalis / Masseter / FOM → facial muscles
- TMJ / temporomandibular joint → jaw joint
- Class III → edge-to-edge bite / underbite
- Periapical pathology → infection at the root of the tooth
- Perio-endo lesion → an infection in the tooth associated with a gum issue
- Medical history → health updates
- Ferrule → band of healthy tooth above the gum line
- Carious lesion → area of decay
- Pulp → nerve
- Infected pulp → damaged nerve tissue
- Radiographs, oral tissues, oral health, Class II — leave these exactly as written; do not substitute a layman's term

═══════════════════════════════════════
STEP 4 — SELF-CHECK (internal only — do not show this in your output)
═══════════════════════════════════════
Before finalizing, silently confirm:
- Every sentence traces back to something explicit in the Patient Notes, Treatment Plan Items, Consent Templates, or Additional Notes.
- No sentence explains a "why" using outside dental knowledge that wasn't stated in the source.
- Every price/fee stated in the source appears in the letter, exactly as written.
- If multiple options were present in the source, each one has its own "### Option N" heading and its own cost line.
- Within each option, re-read every tooth code you wrote: no tooth appears under two different treatments, and each one matches the tooth map from Step 1. If a tooth appears twice in the same option, you have mistaken a flat "teeth involved" list for a treatment list — fix it.
- Every tooth code in the letter appears somewhere in the source notes. You have not introduced a tooth the notes never mention.
- No risk rating has been written up as a present condition: if the notes say only "caries risk: high", the letter does not claim any tooth has decay, a cavity, or a carious lesion.
- Every reason given for a treatment is the reason the notes give. You have not swapped in a more typical-sounding one, and treatments the notes leave unexplained are left unexplained.
- Every material property from Step 1 — lifespan, tooth preparation, appearance, durability — appears in each option using that material. In particular, if the notes give a lifespan for BOTH materials, both lifespans are in the letter; you have not stated one and dropped the other.
- Every clinical term has an inline plain-English explanation at first use, without altering tooth codes, treatment names, or diagnoses.
- The letter is under {word_limit} words.
- There is NO salutation, opening thank-you, or sign-off — the text begins with what was found and ends with the next steps.
If any check fails, revise before responding.

═══════════════════════════════════════
OUTPUT
═══════════════════════════════════════
Output ONLY the finished letter body, in Markdown — no salutation, no sign-off. Do not show the extraction list, the self-check, or any reasoning.

---
Patient Notes:
{patient_notes}

Treatment Plan Items:
{treatment_plan_items}

Consent Templates:
{medicube_templates}

Additional notes:
{additional_notes}
"""

# # Prompt v4
#         self.prompt_template = """
# You are generating a patient-facing dental summary letter from supplied clinical information.

# Your task is a **controlled clinical rewriting task**.

# Your job is to transform the supplied clinical information into clear, warm, professional, patient-friendly language.

# You are **not** being asked to diagnose, interpret, reason clinically, create a treatment plan, or decide what should happen next.

# The final letter must communicate the **same clinical information and clinical meaning as the supplied sources**, using simpler and clearer language.

# ---

# # 1. SOURCE OF TRUTH

# The only sources of clinical information are:

# 1. Patient Notes
# 2. Treatment Plan Items
# 3. Applicable Consent Templates
# 4. Additional Notes

# Treat these sources as authoritative.

# Do not use general dental knowledge to fill gaps.

# Do not add information simply because it would normally be clinically appropriate.

# Do not assume what a dentist would usually do.

# Do not infer information that is not explicitly supported by the supplied sources.

# ---

# # 2. CORE PRINCIPLE

# The output must preserve:

# * the same clinical findings
# * the same diagnoses
# * the same symptoms
# * the same tooth identifiers
# * the same tooth locations
# * the same examination findings
# * the same test results
# * the same treatment choices
# * the same treatment status
# * the same consent status
# * the same recommendations
# * the same advice
# * the same next steps
# * the same timing, when explicitly provided

# Only the following may change:

# * wording
# * sentence structure
# * organisation
# * readability
# * terminology, where permitted by the glossary
# * tone

# Think of the task as:

# **Same clinical facts + same clinical meaning + same status + same consent status + simpler language.**

# ---

# # 3. INTERNAL FACT EXTRACTION — REQUIRED

# Before writing the letter, internally extract the explicitly supported facts from the supplied sources.

# Do not show this extraction to the user.

# For each supported fact, identify where applicable:

# * Clinical finding
# * Diagnosis or condition
# * Symptom
# * Tooth identifier
# * Tooth location
# * Examination finding
# * Test or investigation
# * Test result
# * Treatment
# * Treatment status
# * Consent status
# * Recommendation
# * Advice
# * Referral
# * Next step
# * Timing
# * Other explicitly documented information

# Only record information that is explicitly supported by the supplied sources.

# Do not add clinical interpretations to this internal fact list.

# For example:

# If the source says:

# "LL6 carious lesion. Composite chosen."

# Your internal facts should include:

# * LL6 has a carious lesion.
# * Composite treatment was chosen.

# Do **not** internally convert this into:

# * LL6 has moderate decay.
# * The decay is close to the nerve.
# * The patient consented to treatment.
# * The filling will be placed at the next appointment.
# * Local anaesthetic will be used.

# Those additional statements are not automatically supported.

# ---

# # 4. FACT-LEDGER GENERATION RULE

# After extracting the supported facts, the writing stage becomes **language transformation only**.

# Do not perform additional clinical reasoning during writing.

# Every clinical statement in the final letter must be traceable to at least one explicitly supported fact from the extracted information.

# If a sentence cannot be traced to a supplied fact, remove it.

# A sentence may combine multiple supported facts, but it must not introduce a new fact while doing so.

# Do not make the letter more clinically complete than the supplied information.

# A concise letter with fewer details is preferable to a detailed letter containing unsupported information.

# ---

# # 5. NO CLINICAL INFERENCE

# Do not infer or introduce:

# * diagnoses
# * causes
# * disease severity
# * disease progression
# * prognosis
# * clinical significance
# * treatment indications
# * treatment suitability
# * treatment benefits
# * treatment risks
# * treatment outcomes
# * symptoms
# * absence of symptoms
# * examination methods
# * test interpretations
# * anatomical locations
# * treatment timing
# * appointment timing
# * treatment sequence
# * referrals
# * booking status
# * patient understanding
# * patient agreement
# * consent
# * additional advice
# * follow-up plans

# unless explicitly supported by the supplied sources.

# For example:

# If the notes say:

# "Moderate decay LL6."

# You may write:

# "There is moderate decay in LL6."

# You must not write:

# "The decay is close to the nerve."

# "The decay has not reached the nerve."

# "The tooth needs a filling."

# "The filling will be done at your next appointment."

# "The filling will prevent the decay from getting worse."

# unless those statements are explicitly supported by the supplied sources.

# ---

# # 6. PRESERVE CLINICAL STATUS EXACTLY

# Do not change the status of a treatment or recommendation.

# These are different states:

# * discussed
# * considered
# * recommended
# * offered
# * chosen
# * agreed
# * consented
# * planned
# * scheduled
# * started
# * completed

# Never upgrade or downgrade one state into another.

# For example:

# "Composite chosen"

# must not become:

# "You consented to composite treatment."

# "Composite treatment was agreed"

# must not become:

# "Composite treatment was scheduled."

# "Treatment was discussed"

# must not become:

# "Treatment was planned."

# "Patient agreed to referral"

# must not become:

# "The patient was referred."

# "Patient was referred"

# must not become:

# "The referral appointment was booked."

# Do not assume that a chosen or consented treatment is scheduled.

# Do not assume that a planned treatment has started.

# Do not assume that a referral has been booked.

# Do not assume that a recommendation was accepted.

# ---

# # 7. CONSENT STATUS

# Consent is clinically and legally important.

# Only state that the patient:

# * understood
# * agreed
# * accepted
# * consented
# * gave consent
# * signed consent
# * had consent recorded

# when that specific information is explicitly supported by the supplied sources.

# Do not infer consent from:

# * choosing a treatment
# * discussing a treatment
# * agreeing to consider a treatment
# * having a treatment in the treatment plan
# * receiving a consent template
# * receiving information about treatment

# A consent template provides information about the treatment.

# It does not automatically prove that the patient consented to that treatment.

# ---

# # 8. CONSENT TEMPLATE RULES

# Consent templates may contain generic information about a treatment, such as:

# * what the procedure involves
# * common risks
# * possible benefits
# * alternatives
# * expected aftercare

# Use a matched consent template only when it applies to a treatment explicitly present in the supplied treatment information.

# Template content may explain the treatment in patient-friendly language.

# However, template content must not be used to invent patient-specific facts.

# Do not use a consent template to infer:

# * that the patient has a particular symptom
# * that a procedure has been scheduled
# * that treatment has started
# * that treatment has been completed
# * that the patient consented
# * why the patient selected a treatment
# * the patient's prognosis
# * the patient's expected outcome
# * a specific treatment sequence

# Generic template information must remain generic unless the supplied patient-specific sources explicitly support otherwise.

# ---

# # 9. DO NOT STRENGTHEN CLINICAL LANGUAGE

# Do not make a clinical statement stronger, more certain, or more specific than the source.

# Examples:

# "possible infection"

# must not become:

# "you have an infection."

# "may require further treatment"

# must not become:

# "you will need further treatment."

# "consider extraction"

# must not become:

# "extraction is required."

# "poor prognosis"

# must not become:

# "the tooth cannot be saved."

# "click noted"

# must not become:

# "jaw symptoms were present."

# "patient chose treatment"

# must not become:

# "patient consented to treatment."

# Preserve uncertainty when uncertainty exists.

# ---

# # 10. DO NOT WEAKEN CLINICAL INFORMATION

# Do not remove clinically important specificity simply to make the language easier.

# For example, do not replace a specific diagnosis with a vague phrase if the diagnosis is important.

# The goal is **plain English**, not loss of clinical meaning.

# Clinical terminology may be retained when it is necessary for accuracy.

# Use the glossary below where appropriate.

# ---

# # 11. APPROVED TERMINOLOGY GLOSSARY

# Use these patient-friendly alternatives when they improve readability without changing clinical meaning:

# * Acute → short-term
# * Chronic → long-term
# * Gingivitis → gum disease
# * Periodontitis / periodontal disease → advanced gum disease
# * Gingiva → gums
# * Temporalis / Masseter / FOM → facial muscles
# * TMJ / temporomandibular joint → jaw joint
# * Class III → edge-to-edge bite / underbite
# * Periapical pathology → infection at the root of the tooth
# * Perio-endo lesion → an infection in the tooth associated with a gum issue
# * Medical history → health updates
# * Ferrule → band of healthy tooth above the gum line
# * Carious lesion → area of decay
# * Pulp → nerve
# * Infected pulp → damaged nerve tissue

# Do not apply a glossary replacement if it changes the intended clinical meaning.

# Do not invent a glossary equivalent for terminology that is not listed.

# Do not replace specific treatment names or important clinical diagnoses merely to make the language simpler.

# ---

# # 12. TOOTH IDENTIFIERS

# Preserve every tooth identifier exactly as supplied.

# Do not change:

# * the tooth code
# * upper/lower jaw
# * left/right side
# * tooth number

# Do not silently correct a potentially conflicting tooth description.

# If the supplied source says:

# LL6

# do not rewrite it as LR6.

# Tooth code interpretation:

# * First letter U = upper jaw
# * First letter L = lower jaw
# * Second letter L = left
# * Second letter R = right
# * Number identifies the tooth from the centreline

# Numbering:

# * 1 = central incisor
# * 2 = lateral incisor
# * 3 = canine
# * 4 = first premolar
# * 5 = second premolar
# * 6 = first molar
# * 7 = second molar
# * 8 = third molar

# When a tooth code first appears, you may provide a plain-English description.

# For example:

# "LL6 (lower left first molar)"

# or:

# "UR4 (upper right first premolar)"

# After the first occurrence, the code alone may be used.

# Do not introduce a tooth description that conflicts with the supplied code.

# ---

# # 13. FINDINGS MUST REMAIN FINDINGS

# Do not convert an observation into a diagnosis or interpretation.

# For example:

# "Click noted in the TMJ"

# may become:

# "A click was noted in your jaw joint."

# Do not turn this into:

# "Your jaw joint is unhealthy."

# "You have a jaw disorder."

# "You have jaw symptoms."

# "Your jaw joint needs treatment."

# Similarly:

# "BPE score 3"

# must not automatically become:

# "Your gums have moderate disease."

# unless the supplied source explicitly states that interpretation.

# ---

# # 14. TESTS AND RESULTS

# Preserve test results exactly.

# Do not interpret a test result unless that interpretation is explicitly supplied.

# For example:

# "X-ray showed radiolucency"

# must not automatically become:

# "The X-ray showed an infection."

# "Cold test positive"

# must not automatically become:

# "The tooth has a healthy nerve."

# The letter should communicate what the supplied source says, not what a clinician might infer from it.

# ---

# # 15. RECOMMENDATIONS AND RATIONALE

# Only provide a clinical reason for a recommendation when the reason is explicitly supported by the supplied sources.

# If the source says:

# "Composite chosen due to aesthetics."

# You may state that the patient chose composite for aesthetic reasons.

# If the source only says:

# "Composite chosen."

# Do not invent a reason.

# Do not add generic explanations such as:

# * "to prevent further damage"
# * "to protect the tooth"
# * "to improve your oral health"
# * "to prevent the condition from worsening"
# * "to reduce future risk"

# unless explicitly supported.

# ---

# # 16. ADVICE

# Only include patient advice explicitly supported by the supplied sources or applicable consent information.

# Do not automatically add:

# * brushing advice
# * toothpaste advice
# * flossing advice
# * interdental cleaning advice
# * diet advice
# * smoking advice
# * mouthwash advice
# * pain relief advice
# * sensitivity advice
# * emergency advice

# because they would normally be appropriate.

# Do not invent reassurance or safety advice.

# ---

# # 17. NEXT STEPS AND TIMING

# Only describe future actions when explicitly supported.

# Do not invent:

# * next appointments
# * appointment dates
# * treatment dates
# * number of visits
# * treatment sequences
# * referrals
# * review appointments
# * monitoring plans
# * reassessments

# For example:

# "Composite chosen"

# does not mean:

# "We will place the composite at your next appointment."

# "Referral recommended"

# does not mean:

# "You will be referred."

# "Treatment planned"

# does not mean:

# "Treatment will begin at your next visit."

# ---

# # 18. NO UNSUPPORTED REASSURANCE

# Do not add statements such as:

# * "This is safe."
# * "This is effective."
# * "The procedure is painless."
# * "There is nothing to worry about."
# * "This should resolve the problem."
# * "Your tooth has a good outlook."
# * "The treatment will protect your tooth."

# unless explicitly supported.

# The letter should be reassuring through its tone, not through invented clinical claims.

# ---

# # 19. SIMPLIFICATION WITHOUT CLINICAL CHANGE

# The target reading age is approximately 12.

# Use:

# * short sentences
# * familiar words
# * active voice
# * clear explanations
# * simple sentence structures

# However, readability must never override clinical accuracy.

# Do not simplify by changing the clinical meaning.

# Do not replace a specific clinical condition with an inaccurate general phrase.

# Do not introduce a lay explanation that implies a diagnosis or cause not present in the source.

# ---

# # 20. SENTENCE LENGTH

# Every sentence must contain fewer than 15 words.

# Check sentence length after drafting.

# If a sentence is too long, split it into shorter sentences.

# Do not remove clinical information merely to satisfy the sentence-length requirement.

# ---

# # 21. STRUCTURE

# Keep the letter:

# * warm
# * professional
# * reassuring
# * concise
# * easy to understand

# Use clear headings where appropriate.

# Do not use numbered lists.

# Do not use bullet points.

# Keep the complete letter under 400 words.

# ---

# # 22. PERSONALISATION

# Personalise the letter only using information explicitly supplied in the sources.

# Do not invent:

# * symptoms
# * concerns
# * motivations
# * preferences
# * reasons for treatment choices
# * expectations
# * emotional reactions
# * understanding
# * consent

# Personalisation means making the supplied information patient-facing.

# It does not mean creating a more complete patient story.

# ---

# # 23. CLINICAL NARRATIVE RULE

# Do not create a coherent clinical story by connecting unrelated facts through inference.

# For example, if the sources separately state:

# * tooth wear
# * nightguard discussed

# do not automatically write:

# "You have tooth wear caused by grinding."

# unless grinding is explicitly documented.

# Similarly, do not transform separate treatment items into one combined treatment plan unless the sources explicitly connect them.

# ---

# # 24. REFINEMENT RULE

# After drafting, refine the letter only for:

# * clarity
# * grammar
# * readability
# * organisation
# * sentence length
# * tone
# * repetition

# Do not introduce new clinical information during refinement.

# Do not use refinement as an opportunity to make the letter more clinically complete.

# If a sentence cannot be traced back to the extracted facts, remove it.

# ---

# # 25. FINAL VALIDATION

# Before returning the letter, silently perform this validation.

# For every clinical sentence, ask:

# 1. What supplied fact supports this sentence?
# 2. Is the sentence saying exactly the same clinical thing?
# 3. Did I introduce a diagnosis?
# 4. Did I introduce a symptom?
# 5. Did I introduce a cause?
# 6. Did I introduce severity?
# 7. Did I introduce a test interpretation?
# 8. Did I change a tooth identifier or location?
# 9. Did I change treatment status?
# 10. Did I introduce consent?
# 11. Did I introduce a recommendation?
# 12. Did I introduce a treatment date or appointment?
# 13. Did I introduce a referral or booking?
# 14. Did I introduce advice?
# 15. Did I introduce a benefit, risk, prognosis, or outcome?
# 16. Did I add reassurance that is not supported?
# 17. Did I use general dental knowledge to fill a gap?

# If the answer to any unsupported-content question is yes, remove or rewrite the statement.

# The final letter must contain only source-supported clinical content.

# ---

# # 26. IMPORTANT FINAL RULE

# When information is missing, **leave it missing**.

# Do not guess.

# Do not complete the clinical story.

# Do not make the letter sound more complete by inventing reasonable information.

# A shorter accurate letter is always preferable to a more detailed letter containing unsupported clinical information.

# The objective is:

# **Rewrite the supplied clinical information clearly for the patient.**

# It is not:

# **Decide what the clinical information means or what should happen next.**

# ---

# # 27. LETTER CLOSING

# Where appropriate, retain the existing closing:

# "I've included a few easy-to-read guides..."

# and:

# "We're here to support you..."

# Do not add new clinical claims to the closing.

# ---

# # 28. SOURCE DATA

# Patient Notes:

# {patient_notes}

# Treatment Plan Items:

# {treatment_plan_items}

# Consent Templates:

# {medicube_templates}

# Additional Notes:

# {additional_notes}
# """

# Prompt v3
#         self.prompt_template = """

# Objective:

# Transform the supplied clinical dental information into a clear, structured, warm, and patient-friendly summary letter.

# This is a controlled clinical rewriting task. The purpose is to communicate the supplied information clearly to the patient. It is NOT a clinical reasoning, diagnostic, treatment-planning, or information-generation task.

# The final letter must preserve the clinical information supplied by the authorised sources while making the language easier for the patient to understand.

# Instructions:

# Extract the relevant information from the supplied clinical sources.

# Do not interpret the clinical notes beyond what is explicitly stated or directly supported by the supplied sources.

# Identify relevant details such as:

# * health updates
# * presenting complaint
# * symptoms
# * intraoral and extraoral findings
# * radiographs and test results
# * diagnoses
# * oral hygiene status
# * risk factors
# * treatment information
# * patient preferences
# * consent information
# * agreed treatment plan
# * advice
# * recall interval
# * next steps

# Identify each treatment item within the treatment plan and match it to the appropriate consent clause from the generic database.

# Personalise matched consent clauses only by adapting information that is explicitly supported by the supplied patient notes, treatment plan, consent template, or additional notes.

# Do not use general medical or dental knowledge to fill gaps or add information.

# Use the compiled, source-supported information to generate a structured patient letter. Then refine the wording for clarity, readability, and professional tone without changing the underlying clinical information.

# The letter should summarise, when supported by the supplied sources:

# * What was found during the examination
# * What was discussed
# * What treatment was recommended, chosen, agreed, planned, scheduled, started, or completed
# * The reason for a recommendation, only when explicitly provided
# * Oral hygiene or lifestyle advice
# * Recall interval and next steps

# Do not create information merely to make any of these sections complete.

# SOURCE OF TRUTH AND CLINICAL FIDELITY:

# The following supplied inputs are the only sources of clinical truth:

# 1. Patient Notes
# 2. Treatment Plan Items
# 3. Applicable Consent Templates
# 4. Additional Notes

# Every clinical statement in the final letter must be directly supported by at least one of these sources.

# Do not use your own medical or dental knowledge as an additional source of clinical information.

# Do not add, infer, correct, reinterpret, strengthen, weaken, or complete clinical information using general knowledge.

# If information is not stated or supported by the supplied sources, do not include it.

# Do not fill gaps simply to make the letter more complete, logical, natural, reassuring, or clinically coherent.

# The task is to rewrite the supplied clinical information, not to generate new clinical information.

# CORE PRINCIPLE:

# The final letter must contain:

# Same clinical facts.
# Same clinical meaning.
# Same findings.
# Same test results.
# Same tooth information.
# Same diagnoses.
# Same treatment information.
# Same treatment status.
# Same consent status.
# Same advice.
# Same next steps.

# Only the language, sentence structure, organisation, and readability should change.

# Never improve the clinical content by adding information from general knowledge.

# NO CLINICAL INFERENCE:

# Do not infer or invent:

# * diagnoses
# * causes or causal relationships
# * clinical severity
# * examination methods
# * test results
# * anatomical locations
# * tooth locations
# * treatment indications
# * treatment suitability
# * treatment benefits
# * treatment risks
# * treatment outcomes
# * prognosis
# * treatment timing
# * appointment dates
# * appointment status
# * referral status
# * whether a referral has been completed
# * whether an appointment has been booked
# * whether treatment has started
# * whether treatment has been completed
# * whether treatment is planned
# * whether treatment is scheduled
# * patient understanding
# * patient agreement
# * patient consent
# * additional symptoms
# * additional findings
# * additional advice

# Only include these details when they are explicitly supported by the supplied sources.

# Do not infer a clinical relationship simply because it would be medically or dentally plausible.

# For example, do not turn a symptom and a finding into a diagnosis unless that diagnosis is explicitly supported by the supplied sources.

# Do not describe how an examination or test was performed unless the method is explicitly stated.

# Do not infer why a treatment was selected unless the reason is explicitly provided.

# Do not infer what will happen next unless the next step is explicitly stated.

# TREATMENT STATUS:

# Preserve the exact status of every treatment.

# Do not change one treatment status into another.

# Do not change:

# * discussed → recommended
# * discussed → chosen
# * recommended → chosen
# * recommended → consented
# * chosen → consented
# * chosen → planned
# * consented → planned
# * planned → scheduled
# * scheduled → started
# * started → completed
# * agreed to referral → referred
# * referred → appointment booked
# * appointment booked → treatment completed

# Only use a stronger or different treatment status when that status is explicitly stated in the supplied sources.

# For example:

# If the source says the patient "chose composite fillings", do not write that the fillings "will be placed" unless this is explicitly stated.

# If the source says the patient "agreed to be referred to the hygienist", do not write that the patient "will see the hygienist" unless this is explicitly stated.

# If the source says treatment was "discussed", do not state that the patient agreed to or consented to that treatment unless explicitly supported.

# If the source says treatment is "planned", do not state that it is scheduled unless a schedule is explicitly provided.

# CONSENT STATUS:

# Preserve consent information exactly.

# Do not imply that a patient understood, accepted, agreed to, or consented to treatment unless this is explicitly supported by the supplied sources.

# Do not strengthen medico-legal wording.

# For example, do not change:

# "treatment was discussed"

# into:

# "you understood and consented to treatment"

# unless the supplied sources explicitly support this.

# CONSENT TEMPLATE RULES:

# Consent Templates may provide additional treatment-specific information.

# Use information from a Consent Template only when that template has been matched to the relevant treatment item.

# Do not transfer information from one treatment template to another treatment.

# Do not use information from a consent template to create patient-specific findings that are absent from the Patient Notes.

# Do not use a consent template to infer the patient's diagnosis, symptoms, examination findings, test results, treatment status, appointment status, referral status, or personal circumstances.

# Consent Templates may provide information about:

# * the treatment procedure
# * stated risks
# * stated benefits
# * stated alternatives
# * stated expected effects
# * stated aftercare

# Only include such information when it is contained in the applicable consent template and is relevant to the patient's treatment.

# Do not add risks, benefits, alternatives, procedures, or aftercare from general dental knowledge.

# SOURCE PRIORITY:

# When writing the letter, use the supplied sources as follows:

# * Patient Notes: source of patient-specific clinical findings, symptoms, examination results, diagnoses, and observations.
# * Treatment Plan Items: source of treatment items and their stated treatment status.
# * Consent Templates: source of applicable treatment-specific consent information.
# * Additional Notes: source of any additional explicitly supplied information.

# Do not allow general dental knowledge to override or supplement these sources.

# If two supplied sources contain information that appears inconsistent, do not silently invent a resolution or use general knowledge to correct it.

# Preserve the supplied information according to the existing application logic.

# TOOTH INFORMATION:

# Preserve every tooth identifier exactly as supplied.

# When a tooth code is provided, preserve its associated jaw, side, tooth type, and location as supplied.

# Do not silently change or correct the location associated with a tooth identifier.

# Do not infer a different tooth location from your own dental knowledge.

# If a tooth identifier and a written tooth location appear inconsistent in the supplied information, do not guess which one is correct and do not silently correct the source.

# Always write a tooth code with its plain-English tooth name in brackets after it, for example:

# LL6 (lower molar)
# UR4 (upper premolar)

# Give the plain-English tooth name the first time each tooth is mentioned. After that, the tooth code alone is enough.

# When the supplied tooth code is sufficient to determine the plain-English tooth name, use the following notation:

# * First letter: U = Upper, L = Lower
# * Second letter: R = Right, L = Left
# * Number: tooth position from the centreline
# * 1 = central incisor
# * 2 = lateral incisor
# * 3 = canine
# * 4 and 5 = premolars
# * 6, 7 and 8 = molars

# Use this notation only to provide the plain-English tooth name.

# Do not use it to silently correct conflicting source information.

# LANGUAGE AND READABILITY:

# Use plain English while preserving medical accuracy.

# The finished letter must be readable and understandable by a person with a reading age of approximately 12 years.

# Use short, clear sentences and everyday words wherever possible.

# Every sentence in the letter must contain fewer than 15 words.

# Split longer sentences into two or more shorter sentences.

# Use simple sentence structures.

# Avoid unnecessary technical language.

# Do not simplify language by changing the underlying clinical meaning.

# SIMPLIFICATION WITHOUT CLINICAL CHANGE:

# Only simplify vocabulary, sentence structure, and explanations.

# Do not simplify by changing, weakening, strengthening, replacing, or interpreting the underlying clinical fact.

# Clinical conditions, treatment names, tooth identifiers, findings, test results, measurements, locations, and treatment statuses must remain accurate.

# Simplify the surrounding explanation, not the clinical facts themselves.

# Only replace clinical terms that are too complex for a patient to understand.

# Clinical conditions, treatments, and tooth names that are already understandable to a patient should be preserved.

# GLOSSARY:

# Use the following examples as a guide when a more patient-friendly term is appropriate.

# Term -> Layman's term

# Acute -> short-term

# Chronic -> long-term

# Gingivitis -> gum disease

# Periodontitis / periodontal disease -> advanced gum disease

# Gingiva -> gums

# Temporalis / Masseter / FOM -> facial muscles

# TMJ / temporomandibular joint -> jaw joint

# Class III -> edge-to-edge bite / underbite

# Periapical pathology -> infection at the root of the tooth

# Perio-endo lesion -> an infection in the tooth associated with a gum issue

# Medical history -> health updates

# Ferrule -> band of healthy tooth above the gum line

# Carious lesion -> area of decay

# Pulp -> nerve

# Infected pulp -> damaged nerve tissue

# Do not replace a clinical term merely because a layman's alternative exists.

# Use the layman's term when it improves patient understanding without changing the clinical meaning.

# Do not replace specific treatment names, diagnoses, or tooth identifiers unnecessarily.

# ADVICE:

# Only include oral hygiene, lifestyle, aftercare, or other patient advice when it is explicitly supported by the Patient Notes, applicable Consent Template, Treatment Plan Items, or Additional Notes.

# Do not add advice because it would normally be recommended for the condition or treatment.

# Do not substitute your own advice for advice supplied in the source.

# NEXT STEPS:

# Only include next steps explicitly supported by the supplied sources.

# Do not create future appointments, treatment dates, referral timing, treatment sequences, or actions.

# Do not assume that a treatment will happen at the next appointment unless this is explicitly stated.

# Do not assume that a referral has been completed or an appointment has been booked unless explicitly stated.

# RECOMMENDATIONS AND RATIONALE:

# State recommendations only when they are supported by the supplied sources.

# Include the reason for a recommendation only when that reason is explicitly provided.

# If no reason is provided, do not invent one.

# Do not independently determine which treatment is better, safer, more suitable, stronger, or more effective.

# Do not independently explain clinical consequences that are not present in the supplied sources.

# TONE:

# Warm, professional, and reassuring.

# Use clear, neutral phrasing that inspires trust.

# Do not use reassurance that introduces an unsupported clinical claim.

# Do not say that a treatment is safe, effective, painless, routine, low-risk, or unlikely to cause complications unless this is supported by the supplied sources.

# CONSTRAINTS:

# Keep the letter under 400 words.

# Do not use unexplained abbreviations.

# Use the full term where an abbreviation is not patient-friendly.

# Do not use numbering or bullet points in the final patient letter. Use paragraphs and headings instead.

# Do not add information solely to make the letter sound more complete.

# Do not add information solely to make the letter sound more professional.

# Do not add information solely to make the letter sound more reassuring.

# Do not add information solely because it is clinically likely or normally recommended.

# FINAL VALIDATION:

# Before producing the final letter, silently check every clinical statement.

# For each statement, ask:

# 1. Is this statement directly supported by the supplied sources?
# 2. Did I add any clinical fact?
# 3. Did I infer anything that was not explicitly stated?
# 4. Did I introduce a diagnosis that was not supplied?
# 5. Did I introduce a cause or clinical relationship that was not supplied?
# 6. Did I change any tooth identifier or location?
# 7. Did I invent an examination method?
# 8. Did I change the treatment status?
# 9. Did I strengthen the consent status?
# 10. Did I invent appointment timing?
# 11. Did I invent referral status?
# 12. Did I invent treatment completion?
# 13. Did I add unsupported risks or benefits?
# 14. Did I add unsupported advice?
# 15. Did I change the clinical meaning while simplifying the language?
# 16. Did I introduce information from general dental knowledge?

# If the answer to any question is yes, remove or correct the unsupported statement before producing the letter.

# The final output must be a faithful patient-friendly rewriting of the supplied information.

# FEW-SHOT EXAMPLE:

# Do not use a few-shot example to introduce clinical facts, risks, benefits, advice, diagnoses, or treatment rationale that are not present in the supplied inputs.

# If a few-shot example is provided by the application, treat it only as an example of writing style, structure, and reading level.

# Never copy clinical facts from the few-shot example into the patient's letter unless those facts are explicitly present in the current patient's supplied sources.

# Response Format:

# Structure the letter using:

# Greeting and thanks

# Summary of findings

# Treatment discussed and chosen, where supported

# Advice, where supported

# Next steps, where supported

# Sign-off with clinician

# Do not add a section simply because no information is available for it.

# Recap:

# Create a friendly, clear, structured patient letter from the supplied dental information.

# The letter should be easy for a patient with a reading age of approximately 12 years to understand.

# Preserve the clinical facts, clinical meaning, tooth information, treatment status, consent status, advice, and next steps.

# Do not interpret, diagnose, infer, predict, or add clinical information.

# Do not use general dental knowledge to fill gaps.

# The final letter must be a simplified rewrite of the supplied information, not a newly generated clinical narrative.

# Patient Notes:

# {patient_notes}

# Treatment Plan Items:

# {treatment_plan_items}

# Consent Templates:

# {medicube_templates}

# Additional Notes:

# {additional_notes}

# """





    @staticmethod
    def _has_multiple_options(patient_notes: str) -> bool:
        """
        Heuristic check for whether the patient notes describe two or more
        distinct treatment options the patient is choosing between (e.g.
        "1) ... 2) ..." or "option 1 / option 2").
        """
        text = patient_notes or ""
        numbered = set(re.findall(r'(?m)^\s*\(?([1-9])\)\s', text))
        option_words = set(w.lower() for w in re.findall(r'(?i)\boption\s*[1-9]\b', text))
        return len(numbered) >= 2 or len(option_words) >= 2

    @classmethod
    def _compute_word_limit(cls, patient_notes: str, base_limit: int = 400, multiplier: float = 1.3) -> int:
        """
        Compute the word limit to hand to the prompt as a literal number.
        Multiple treatment options need more room to describe separately,
        so the limit is raised by `multiplier` — this is calculated here in
        code rather than asking the model to "increase by 30%" itself.
        """
        if cls._has_multiple_options(patient_notes):
            return round(base_limit * multiplier)
        return base_limit

    # Openers like "Dear Tom," / "Thank you for attending your appointment today."
    _GREETING_PATTERNS = (
        re.compile(r'(?i)^dear\b[^\n]*$'),
        re.compile(r'(?i)^(thank you|thanks)\b[^\n]*\b(attend|attending|coming|came|visit|visiting|appointment|consultation|seeing us|for your time)\b[^\n]*$'),
        re.compile(r'(?i)^(it was|thank you for)\b[^\n]*\b(pleasure|lovely|good) to (see|meet)\b[^\n]*$'),
    )

    # Sign-offs like "Warm regards," / "Yours sincerely," — these end the letter,
    # so everything from the match onwards (the closing plus the name) is dropped.
    _SIGN_OFF_PATTERN = re.compile(
        r'(?im)^\s*('
        r'(warm|kind|best|warmest)\s+(regards|wishes)'
        r'|yours\s+(sincerely|faithfully|truly)'
        r'|sincerely|regards|best\s+wishes'
        r')\s*[,.]?\s*$'
    )

    @classmethod
    def strip_greeting_and_sign_off(cls, text: str) -> str:
        """
        Remove any salutation, opening thank-you, or sign-off the model wrote.

        The prompt tells the model not to write them, but models drift, so this
        is enforced in code: `add_greeting_and_sign_off` always adds its own
        greeting and sign-off, and anything the model produced would otherwise
        appear alongside it as a duplicate. Only recognisable greeting/sign-off
        lines are touched — clinical prose is never matched.
        """
        if not text:
            return text

        # Drop the sign-off and everything after it (the closing plus the name).
        match = cls._SIGN_OFF_PATTERN.search(text)
        if match:
            text = text[:match.start()]

        # Drop leading salutation/thank-you paragraphs, one at a time.
        paragraphs = re.split(r'\n\s*\n', text.strip())
        while paragraphs:
            first = paragraphs[0].strip()
            if any(p.match(first) for p in cls._GREETING_PATTERNS):
                paragraphs.pop(0)
                continue
            break

        return "\n\n".join(paragraphs).strip()

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
        word_limit = self._compute_word_limit(patient_notes)

        prompt = self.prompt_template.format(
            patient_notes=patient_notes or "",
            treatment_plan_items="\n".join(treatment_plan_items or []),
            medicube_templates="\n".join(medicube_templates or []),
            additional_notes=additional_notes or "",
            word_limit=word_limit
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

        processed_text = self.strip_greeting_and_sign_off(processed_text)
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
