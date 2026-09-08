import re
import openai
import markdown
from typing import List, Tuple
from .post_processor import MarkdownPostProcessor
from .models import LetterRequest, LetterResponse


# Letter styles. The clinical rules of the prompt are identical for both — only
# the presentation of each section's content differs, so the two styles are
# built from ONE template with these fragments swapped in. Keeping a single
# template means a fix to a grounding or tooth-mapping rule applies to both
# styles at once, instead of having to be made twice and drifting apart.
LETTER_STYLES = {
    "standard": {
        "label": "Standard",
        "description": "Paragraphs throughout, with the treatment options set out as bullets so they can be compared.",
        "content_rule": (
            'The content inside each section is written as flowing paragraphs of plain English — short sentences joined '
            'into a paragraph that reads naturally when read aloud. Patients find continuous prose easier to read than '
            'fragmented lists, so do NOT use bullet points in the findings, discussion, next steps, recommendations or '
            'homecare sections. There is ONE exception: the "## Treatment Options" section, where the patient is '
            'weighing choices against each other and bullet points are required — see the formatting rules below. '
            'Section headings are used throughout, in both cases.'
        ),
        "findings_rule": (
            "Write the findings as a flowing paragraph rather than a list — every finding still has to be there, it is "
            "only the presentation that changes."
        ),
        "option_rule": (
            "- Under each option's sub-heading, set out what it involves as SHORT BULLET POINTS — which teeth, which "
            "material, what the treatment includes, how long the material lasts, what preparation it needs, and what "
            "extra stages it involves. This is the ONE place in the letter where bullets are used, because the patient "
            "is comparing the options side by side and a dense paragraph is much harder to weigh up.\n"
            "- If the notes describe only ONE treatment path, there is nothing to compare: describe it in paragraphs "
            "under \"## Treatment Recommended\", with no bullet points and no \"### Option N\" sub-headings."
        ),
        "writing_rule": (
            "- Use short sentences joined into short paragraphs everywhere except the treatment options, which are "
            "bulleted. Do not use bullet points or numbered lists in any other section."
        ),
        "example": """CORRECT — note that every section is written as paragraphs EXCEPT the treatment options, which are bulleted so the patient can compare them, each with its cost on its own line:

## Examination Findings
Your oral hygiene is good. The LR5 and LL5 need crowns, and the UR6 needs a filling.

## Discussion
We talked through the two crown materials. A metal crown lasts about 20 years but needs more tooth preparation, while a ceramic crown lasts about 10 years and needs less. To match the LR5, I would also crown the LR4.

## Treatment Options

### Option 1: Crowns and a filling
- Crowns on the LR4, LR5 and LL5.
- A filling on the UR6.

Estimated cost: £820.

### Option 2: Crowns on all four teeth
- Crowns on the LR4, LR5, LL5 and UR6.
- A longer-lasting result.

Estimated cost: £2,400.

You have not yet decided which option to go for.

## Next Steps
A review appointment has been booked to decide which option you would like.

## Homecare Advice
Cutting down on fizzy drinks will help protect your teeth.""",
    },
    "bulleted": {
        "label": "Bulleted",
        "description": "Findings and options broken into short bullet points for quick scanning.",
        "content_rule": (
            'The content inside each section is plain English — short sentences and short paragraphs — and may use bullet '
            'points wherever a list is clearer to read than a sentence (several findings, several pieces of advice, the '
            'parts of a planning stage). "Plain prose" describes how the content should READ; it is never a reason to '
            'leave out a section heading, and never a reason to cram a list into one long sentence.'
        ),
        "findings_rule": "Where there are several distinct findings, list them as bullet points.",
        "option_rule": (
            "- Under each option's sub-heading, describe what it involves — which teeth, which material, what the "
            "treatment includes. Use bullet points wherever they make the option easier to compare (what is covered, how "
            "long the material lasts, what preparation it needs, what extra stages it involves). A dense paragraph is "
            "harder to weigh up than a short list."
        ),
        "writing_rule": (
            "- Use short sentences and short paragraphs throughout, and bullet points wherever a list reads more clearly "
            "than a sentence."
        ),
        "example": """CORRECT — note the section headings, the bullet points inside an option, and the cost on its own line:

## Examination Findings
- Your oral hygiene is good.
- The LR5 and LL5 need crowns, and the UR6 needs a filling.

## Discussion
We talked through the two crown materials. A metal crown lasts about 20 years but needs more tooth preparation, while a ceramic crown lasts about 10 years and needs less. To match the LR5, I would also crown the LR4.

## Treatment Options

### Option 1: Crowns and a filling
- Crowns on the LR4, LR5 and LL5.
- A filling on the UR6.

Estimated cost: £820.

### Option 2: Crowns on all four teeth
- Crowns on the LR4, LR5, LL5 and UR6.
- A longer-lasting result.

Estimated cost: £2,400.

You have not yet decided which option to go for.

## Next Steps
A review appointment has been booked to decide which option you would like.

## Homecare Advice
Cutting down on fizzy drinks will help protect your teeth.""",
    },
    "narrative": {
        "label": "Narrative",
        "description": "The same letter written as flowing paragraphs, with no bullet points.",
        "content_rule": (
            'The content inside each section is written as flowing paragraphs of plain English — short sentences joined '
            'into a paragraph that reads naturally when spoken aloud. Do NOT use bullet points, numbered lists, or dashes '
            'to split the content into fragments. Where several findings or several features of an option belong '
            'together, write them as connected sentences within one paragraph. This applies to the CONTENT only: the '
            'section headings themselves stay exactly as specified below.'
        ),
        "findings_rule": (
            "Where there are several distinct findings, join them into a flowing paragraph rather than listing them — "
            "every finding still has to be there, it is only the presentation that changes."
        ),
        "option_rule": (
            "- Under each option's sub-heading, describe what it involves in flowing sentences — which teeth, which "
            "material, what the treatment includes, how long the material lasts, what preparation it needs, and what "
            "extra stages it involves. Write this as a short paragraph rather than a bullet list, keeping the sentences "
            "short so the patient can still weigh the options against each other."
        ),
        "writing_rule": (
            "- Use short sentences joined into short paragraphs. Do not use bullet points, numbered lists or dashes "
            "anywhere in the letter body — the only markdown is the section and option headings."
        ),
        "example": """CORRECT — note the section headings, the flowing paragraphs inside each option, and the cost on its own line:

## Examination Findings
Your oral hygiene is good. The LR5 and LL5 need crowns, and the UR6 needs a filling.

## Discussion
We talked through the two crown materials. A metal crown lasts about 20 years but needs more tooth preparation, while a ceramic crown lasts about 10 years and needs less. To match the LR5, I would also crown the LR4.

## Treatment Options

### Option 1: Crowns and a filling
This option places crowns on the LR4, LR5 and LL5, and a filling on the UR6.

Estimated cost: £820.

### Option 2: Crowns on all four teeth
This option places crowns on the LR4, LR5, LL5 and UR6, and gives a longer-lasting result.

Estimated cost: £2,400.

You have not yet decided which option to go for.

## Next Steps
A review appointment has been booked to decide which option you would like.

## Homecare Advice
Cutting down on fizzy drinks will help protect your teeth.""",
    },
}

# "standard" is the format the dentists asked for: prose letters, with bullets
# used only where multiple treatment options need to be compared. The other two
# are kept selectable for comparison.
DEFAULT_LETTER_STYLE = "standard"


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
        self.prompt_template_base = """
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

COUNTING TEETH IN AN OPTION:
- "top and bottom 4 teeth", "upper and lower 4 teeth", "4 top and bottom" all mean FOUR IN EACH ARCH — four upper PLUS four lower, eight teeth in total. They never mean four teeth altogether. Write this as "the four upper and four lower front teeth" so the patient cannot misread it either.
- Keep exactly the count the notes give. Never shrink a per-arch count into a total, and never expand a total into a per-arch count.
- Where the notes describe an option only by a count or a region ("the top and bottom 4 teeth", "the upper front teeth"), describe it the same way. Do NOT name specific tooth codes for that option: the notes have not said which teeth they are, so naming them invents clinical detail. Use tooth codes only where the notes give them for that option.
- Teeth named elsewhere in the notes, for a different option or a different part of the discussion, do not carry over. Each option covers exactly the teeth the notes give for that option.

═══════════════════════════════════════
STEP 2 — DECIDE THE STRUCTURE
═══════════════════════════════════════
Look at what you extracted in Step 1:
- If the notes describe TWO OR MORE distinct treatment options that the patient is choosing between (e.g. "option 1 / option 2", "or", a numbered list of alternatives), each option MUST get its own subsection in the "Treatment options" part of the letter — see the formatting rules and worked example below.
- If there is only one treatment path, describe it under a single "## Treatment Recommended" heading, with no "### Option N" sub-headings.

═══════════════════════════════════════
STEP 3 — WRITE THE LETTER
═══════════════════════════════════════
Using ONLY the facts from Step 1, write the BODY of a letter using the section structure below, in this order. EVERY section gets its own heading, written as "## <Section name>" on its own line.

<<STYLE_CONTENT_RULE>>

## Examination Findings
What was found when the patient was examined. Include EVERY finding and risk rating from Step 1 — the bite/occlusion and any measurement such as an overjet are findings and belong here just as much as the teeth themselves. Do not shorten this section by dropping findings; a finding the notes recorded is a finding the patient is told about. <<STYLE_FINDINGS_RULE>>

## Discussion
What was talked through with the patient after the examination: what the findings mean for them, why treatment is being suggested, and any comparison of materials or approaches the notes record (for example how long each material lasts, or which needs tooth preparation). Use only the reasoning present in the source, never your own.

## Treatment Options
The choices the patient is deciding between. Each option gets its own "### Option N: <short name>" sub-heading underneath this section heading — see the formatting rules below.

## Next Steps
What happens next: the review or next appointment, what will be decided or done at it, and the recall interval if one is stated.

## Recommendations
Anything the clinician recommended alongside or before the treatment itself, with the reason the notes give (for example whitening before restorative work, because restorations cannot be whitened afterwards).

## Homecare Advice
Oral hygiene, diet, or lifestyle advice the patient should follow at home.

OMIT ANY SECTION THE NOTES GIVE NO CONTENT FOR. A section heading with nothing real underneath it is worse than no section: never invent findings, advice, recommendations or next steps to fill one. If the notes contain no homecare advice, there is no Homecare Advice section — the heading is absent too.
Do NOT write the heading and then report that there is nothing to say. Lines such as "(There is no additional home-care advice recorded.)", "None recorded.", or "Not applicable." must never appear in the letter. The patient should not be shown an empty section at all; simply move on to the next one that does have content.

DO NOT write a salutation, greeting, opening thank-you, or sign-off. Specifically, do not begin with "Dear ...", "Thank you for attending/coming in ...", or any similar opening line, and do not end with "Warm regards", "Kind regards", "Yours sincerely", or the clinician's name. The greeting and sign-off are added automatically after you finish — anything you write of that kind is duplicated in the final letter. Start directly with the "## Examination Findings" heading.

FORMATTING RULES FOR THE "## Treatment Options" SECTION:
- If Step 2 found multiple options: under the "## Treatment Options" heading, give each option its own sub-heading on its own line, written EXACTLY as "### Option 1: <short name>" — three hash characters, then the option number, then a short name (numbered in the order the source presents them).
- The "### Option N" sub-heading is required for every option. Do NOT instead write the option name in bold ("**Option 1: ...**") or as a plain sentence. Each option must be visibly set apart from the others, because the patient is comparing them side by side.
<<STYLE_OPTION_RULE>>
- STATE THE COST OF EVERY OPTION CLEARLY, on its own line at the end of that option, exactly as the notes give it — for example "Estimated cost: £1,106." Never round, merge or omit a figure, and never leave the patient to infer which option a price belongs to. If the notes give a price for an option, that price appears under that option.
- CARRY MATERIAL PROPERTIES INTO EVERY OPTION THAT USES THAT MATERIAL. If Step 1 recorded a property for a material — how long it lasts, whether it needs tooth preparation, its appearance or durability — it MUST appear in each option using that material, even though the notes state it only once and somewhere else entirely (typically in the discussion, not in the numbered option). The patient is choosing between these options largely on how long each lasts, so a stated lifespan is never optional. If the notes give a lifespan for one material, the option using the other material must carry its stated lifespan too — never state one and omit the other.
- Include only properties the source actually states — never invent generic pros/cons.
- If there is only one treatment path: describe it under a "## Treatment Recommended" heading instead, in plain English, with no "### Option N" sub-headings. Still state its cost exactly as given if the source contains one.

WORKED EXAMPLE (structure, formatting and tooth-mapping only — these clinical facts are illustrative and must NEVER appear in a real letter; the teeth and figures below are deliberately different from any real case):

Patient notes: "O/E oh good. crowns needed on the LR5 and LL5, and a filling on the UR6. In order to match the LR5 I would also do the LR4 crown. crown types: metal crown (lasts 20 years, more prep) vs ceramic crown (lasts 10 years, less prep). pt unsure which to go for - can do either options: 1) crown / filling mix on the LR4, LR5, LL5 and UR6 teeth, total cost £820  2) crowns on all four teeth, £2400, longer lasting. rv booked. advised to cut down fizzy drinks."

Step 1 tooth map, taken from the DETAILED sentence (not the flat list):
- crown → LR5, LL5, LR4
- filling → UR6
The flat list in option 1 ("LR4, LR5, LL5 and UR6") is only the set of teeth INVOLVED. UR6 stays a filling there. In option 2 the source explicitly says crowns on all four, so UR6 becomes a crown in that option only.

WRONG (never do this — UR6 is double-booked as both a crown and a filling, the option name is bold instead of a "### Option N" sub-heading, and the cost is buried mid-sentence):

**Option 1: Crowns and a filling** – This involves crowns on the LR4, LR5, LL5 and UR6, and a filling on the UR6 costing £820.

<<STYLE_EXAMPLE>>

(There is no Recommendations section in this example because these notes record none — sections without content in the notes are simply left out.)

GENERAL WRITING RULES:
- Write for a reader with no medical background — aim for a reading level a 12-year-old could follow comfortably.
- The first time any clinical term appears, explain it immediately in plain words, e.g. "gum disease (gingivitis)." Use the glossary below where it applies. Never use an abbreviation without spelling it out in full at first use.
- Do not replace a specific tooth code (e.g. "UR1"), treatment name (e.g. "composite veneer," "root canal treatment"), or diagnosis with a vague substitute — only simplify genuine jargon, not clinical specifics.
<<STYLE_WRITING_RULE>>
- Keep the full letter under {word_limit} words.
- Tone: warm, professional, reassuring — never alarming, never clinical or cold.

CLINICAL SHORTHAND — notes are written fast, in abbreviations, and often with typos. Read through the shorthand and the spelling mistakes; a finding written in shorthand is still a finding and must not be skipped because it was hard to read:
- O/E, o/e → on examination
- OH → oral hygiene
- MH → medical history
- PCO, C/O → the patient's own concern or complaint
- OJ → overjet (how far the upper front teeth sit ahead of the lower ones); "2mm OJ" is a 2 mm overjet
- occ → occlusion, i.e. the bite
- Class I / Class II / Class III, with "div I" or "div II" → the classification of the bite; report it as written (e.g. "a Class II division I bite"), and treat it as a finding
- rv → review appointment
- pt → patient
- Dw pt → discussed with the patient
- BPE → gum health screening score
Typos in the notes ("LCass II" for "Class II", "emax"/"e.max", "yars" for "years") do not change the meaning — read the intended term and write it correctly in the letter.

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
- Every section present has a "## <Section name>" heading, following the Step 3 structure and order: Examination Findings, Discussion, Treatment Options, Next Steps, Recommendations, Homecare Advice. Sections the notes give no content for are absent entirely — none has been padded with invented content.
- No section says there is nothing to report. If a section would have contained a line like "(There is no home-care advice recorded.)" or "None recorded.", that whole section — heading included — has been deleted instead.
- If multiple options were present in the source, they sit under "## Treatment Options", and each has its own "### Option N: ..." sub-heading — three hash characters, not bold text and not a plain sentence.
- Every option states its cost on its own line, exactly as the notes give it, and the price sits under the option it belongs to.
- Within each option, re-read every tooth code you wrote: no tooth appears under two different treatments, and each one matches the tooth map from Step 1. If a tooth appears twice in the same option, you have mistaken a flat "teeth involved" list for a treatment list — fix it.
- Every tooth code in the letter appears somewhere in the source notes. You have not introduced a tooth the notes never mention.
- No risk rating has been written up as a present condition: if the notes say only "caries risk: high", the letter does not claim any tooth has decay, a cavity, or a carious lesion.
- Every reason given for a treatment is the reason the notes give. You have not swapped in a more typical-sounding one, and treatments the notes leave unexplained are left unexplained.
- Every material property from Step 1 — lifespan, tooth preparation, appearance, durability — appears in each option using that material. In particular, if the notes give a lifespan for BOTH materials, both lifespans are in the letter; you have not stated one and dropped the other.
- Every tooth count matches the notes: an option covering four teeth in each arch says "four upper and four lower" (eight), not "four front teeth". No option names specific tooth codes that the notes did not give for that option.
- Every finding from Step 1 reached the letter, including any written in shorthand — if the notes record a bite classification or an overjet measurement, the letter states it.
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

        # Default style, kept as `prompt_template` so existing callers are unaffected.
        self.prompt_template = self.build_prompt_template(DEFAULT_LETTER_STYLE)



    def build_prompt_template(self, style: str = DEFAULT_LETTER_STYLE) -> str:
        """
        Build the prompt for a letter style by substituting that style's
        presentation fragments into the shared template.

        Only the presentation of each section's content differs between styles;
        every clinical rule — grounding, tooth mapping, tooth counts, risk vs
        finding, material properties — is shared, so a fix to any of those
        applies to all styles at once.
        """
        if style not in LETTER_STYLES:
            raise ValueError(
                f"Unknown letter style {style!r}. Available: {', '.join(sorted(LETTER_STYLES))}"
            )
        fragments = LETTER_STYLES[style]
        template = self.prompt_template_base
        for token, key in (
            ("<<STYLE_CONTENT_RULE>>", "content_rule"),
            ("<<STYLE_FINDINGS_RULE>>", "findings_rule"),
            ("<<STYLE_OPTION_RULE>>", "option_rule"),
            ("<<STYLE_WRITING_RULE>>", "writing_rule"),
            ("<<STYLE_EXAMPLE>>", "example"),
        ):
            if token not in template:
                raise ValueError(f"Prompt template is missing the {token} placeholder")
            template = template.replace(token, fragments[key])
        return template

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
    def _compute_word_limit(cls, patient_notes: str, base_limit: int = 550, multiplier: float = 1.3) -> int:
        """
        Compute the word limit to hand to the prompt as a literal number.
        Multiple treatment options need more room to describe separately,
        so the limit is raised by `multiplier` — this is calculated here in
        code rather than asking the model to "increase by 30%" itself.

        The base was raised from 400 to 550 when the letter gained its full
        section structure (findings, discussion, options, next steps,
        recommendations, homecare). Letters were already running 395-450
        words with only some of those sections, and when the limit binds the
        model drops content rather than tightening it — which is how the
        bite finding went missing before. The 1.3 multiplier is unchanged.
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
        temperature: float = 0.0,
        style: str = DEFAULT_LETTER_STYLE
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
            style: Letter style — "bulleted" (default) or "narrative"

        Returns:
            Tuple of (sections, full_letter, processed_html)
        """
        word_limit = self._compute_word_limit(patient_notes)

        prompt = self.build_prompt_template(style).format(
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
