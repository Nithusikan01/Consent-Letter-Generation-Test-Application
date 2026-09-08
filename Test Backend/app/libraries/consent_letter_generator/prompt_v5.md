# Consent letter prompt — v5

Addresses dentist feedback from `Feedback on the Letter Generator.pdf` (2026-09-07):
1. Pricing was missing from generated letters.
2. Multiple treatment options were blended into one paragraph instead of being presented separately.
3. When multiple options are shown, the word limit should be 130% of normal — computed in code, not requested as "increase by 30%" in the prompt.

Also reintroduces a glossary (dropped in the currently deployed prompt), refreshed against the dentist's updated jargon table.

Companion code changes: `generator.py` now computes `word_limit` in Python (`_compute_word_limit`) before formatting this template, and `post_processor.py`'s `_llm_cleanup` step no longer flattens headings/bullets/tables back into paragraphs (it previously undid any structure this prompt produced).

## System message

```
You are a clinically trained dental copywriter who specialises in patient communication.
```

## User prompt template

```
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

The content inside each section is plain English — short sentences and short paragraphs — and may use bullet points wherever a list is clearer to read than a sentence (several findings, several pieces of advice, the parts of a planning stage). "Plain prose" describes how the content should READ; it is never a reason to leave out a section heading, and never a reason to cram a list into one long sentence.

## Examination Findings
What was found when the patient was examined. Include EVERY finding and risk rating from Step 1 — the bite/occlusion and any measurement such as an overjet are findings and belong here just as much as the teeth themselves. Do not shorten this section by dropping findings; a finding the notes recorded is a finding the patient is told about. Where there are several distinct findings, list them as bullet points.

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

OMIT ANY SECTION THE NOTES GIVE NO CONTENT FOR. A section heading with nothing real underneath it is worse than no section: never invent findings, advice, recommendations or next steps to fill one. If the notes contain no homecare advice, there is no Homecare Advice section.

DO NOT write a salutation, greeting, opening thank-you, or sign-off. Specifically, do not begin with "Dear ...", "Thank you for attending/coming in ...", or any similar opening line, and do not end with "Warm regards", "Kind regards", "Yours sincerely", or the clinician's name. The greeting and sign-off are added automatically after you finish — anything you write of that kind is duplicated in the final letter. Start directly with the "## Examination Findings" heading.

FORMATTING RULES FOR THE "## Treatment Options" SECTION:
- If Step 2 found multiple options: under the "## Treatment Options" heading, give each option its own sub-heading on its own line, written EXACTLY as "### Option 1: <short name>" — three hash characters, then the option number, then a short name (numbered in the order the source presents them).
- The "### Option N" sub-heading is required for every option. Do NOT instead write the option name in bold ("**Option 1: ...**") or as a plain sentence. Each option must be visibly set apart from the others, because the patient is comparing them side by side.
- Under each option's sub-heading, describe what it involves — which teeth, which material, what the treatment includes. Use bullet points wherever they make the option easier to compare (what is covered, how long the material lasts, what preparation it needs, what extra stages it involves). A dense paragraph is harder to weigh up than a short list.
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

> **Option 1: Crowns and a filling** – This involves crowns on the LR4, LR5, LL5 and UR6, and a filling on the UR6 costing £820.

CORRECT — note the section headings, the bullet points inside an option, and the cost on its own line:

> ## Examination Findings
> - Your oral hygiene is good.
> - The LR5 and LL5 need crowns, and the UR6 needs a filling.
>
> ## Discussion
> We talked through the two crown materials. A metal crown lasts about 20 years but needs more tooth preparation, while a ceramic crown lasts about 10 years and needs less. To match the LR5, I would also crown the LR4.
>
> ## Treatment Options
>
> ### Option 1: Crowns and a filling
> - Crowns on the LR4, LR5 and LL5.
> - A filling on the UR6.
>
> Estimated cost: £820.
>
> ### Option 2: Crowns on all four teeth
> - Crowns on the LR4, LR5, LL5 and UR6.
> - A longer-lasting result.
>
> Estimated cost: £2,400.
>
> You have not yet decided which option to go for.
>
> ## Next Steps
> A review appointment has been booked to decide which option you would like.
>
> ## Homecare Advice
> Cutting down on fizzy drinks will help protect your teeth.

(There is no Recommendations section in this example because these notes record none — sections without content in the notes are simply left out.)

GENERAL WRITING RULES:
- Write for a reader with no medical background — aim for a reading level a 12-year-old could follow comfortably.
- The first time any clinical term appears, explain it immediately in plain words, e.g. "gum disease (gingivitis)." Use the glossary below where it applies. Never use an abbreviation without spelling it out in full at first use.
- Do not replace a specific tooth code (e.g. "UR1"), treatment name (e.g. "composite veneer," "root canal treatment"), or diagnosis with a vague substitute — only simplify genuine jargon, not clinical specifics.
- Use short sentences and short paragraphs throughout, and bullet points wherever a list reads more clearly than a sentence.
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
```

## Word-limit inputs (computed in code, not requested as a percentage)

`{word_limit}` is filled in by `ConsentLetterGenerator._compute_word_limit()`:

- Base case: `400` words (per the project spec's "under 400 words").
- Multiple options detected in `patient_notes` (via `_has_multiple_options`, a regex check for `1)`/`2)`-style enumerations or `option 1`/`option 2` wording): `round(400 * 1.3)` = `520` words.

The prompt only ever sees a literal number (e.g. "under 520 words") — it is never told to calculate a percentage increase itself, per the dentist's explicit instruction.

## Known limitation

`_has_multiple_options` is a regex heuristic tuned to the patterns in the dentist's own example. If clinician shorthand varies too much for this to hold up, replace it with a small separate classification call (ask the model to report how many distinct options are being compared) rather than expanding the regex indefinitely.
