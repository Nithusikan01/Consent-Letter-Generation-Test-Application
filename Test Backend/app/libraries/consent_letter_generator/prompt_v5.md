# Consent letter prompt — v5

## Format

Paragraphs throughout, with the treatment options set out as bullet points only
when there are two or more of them to compare (Dr. Sahan, 2026-09-08: dentists
find bulleted letters harder for patients to read; bullets are wanted only where
options are being compared). With exactly one treatment path there is nothing to
compare, so that section is written in paragraphs too, under a
"## Treatment Recommended" heading with no "### Option N" sub-headings.

This was previously offered as one of three selectable styles ("standard",
"bulleted", "narrative"). The other two have been removed, along with the style
selector in the test UI and the extra backend endpoints, now that the format is
confirmed. The template below is the single prompt in current use.

## Options, choices and stages

Three rules govern the Treatment Options section, added after manual testing
found letters silently dropping content:

- **A choice does not delete the alternatives.** Where the notes discuss several
  options and then record one as chosen or recommended — commonly under a
  "For pt has chosen" heading — the letter still sets out every option with its
  own cost, and states the choice in one sentence *after* them. Letters were
  collapsing to the chosen option alone, so the patient no longer saw what else
  was offered or what it would have cost.
- **Options are alternatives; stages are not.** Work described as
  "Stage 1 / Stage 2 / Stage 3", or several treatments all being carried out,
  is one plan in parts — presented under "## Treatment Recommended" in order,
  never as "### Option N", which would wrongly invite the patient to pick one.
- **Price qualifiers are part of the price.** "from £3,200", "£220 each",
  "£95 per maintenance visit" and "total estimated cost: £325" are never reduced
  to bare figures.

The notes' own headings ("Dw pt", "For pt has chosen", "Risk assessment",
"PCO", "O/e") are input structure only and never appear in the letter; their
content is redistributed into the letter's own sections.

## Feedback addressed

Addresses dentist feedback from `Feedback on the Letter Generator.pdf` (2026-09-07):
1. Pricing was missing from generated letters.
2. Multiple treatment options were blended into one paragraph instead of being presented separately.
3. When multiple options are shown, the word limit should be 130% of normal — computed in code, not requested as "increase by 30%" in the prompt.

Also reintroduces a glossary (dropped in the currently deployed prompt), refreshed against the dentist's updated jargon table.

Companion code changes: `generator.py` computes `word_limit` in Python (`_compute_word_limit`) before formatting this template. `post_processor.py` no longer makes an LLM call at all — its `_llm_cleanup` step was removed (see the token budget below); the deterministic heading/bullet/numbering passes remain, and greeting removal and heading levels are enforced in `generator.py`.

## Token budget (Groq free tier: 8,000 tokens per minute)

The prompt has to leave room for the notes and the letter inside a single
minute's allowance, counted across input and output together. Figures below are
measured from real Groq responses, not estimated:

| | tokens |
| --- | --- |
| This template | ~5,700 |
| Patient notes (agreed maximum) | 700 |
| System message | ~20 |
| Reasoning (see below) | 400–850 |
| Letter itself | 100–750 |
| **Worst case total** | **~7,900 of 8,000** |

Two changes made that fit. The prompt was cut from ~6,800 to ~5,700 tokens by
removing decorative separator lines, compressing the self-check into terse
imperatives (no check was dropped), and de-duplicating the option rules that had
been stated in Step 2, the formatting rules and the self-check alike. Separately,
the post-processing LLM call was removed: it cost ~1,600 tokens of the same
minute — enough on its own to breach the limit — while duplicating the
deterministic passes.

### Completion settings — `max_completion_tokens = 1500`, `reasoning_effort = "low"`

Two constraints pull against each other here, and both were hit in testing.

**Groq reserves `max_completion_tokens`.** The figure it rate-limits against is
`prompt + cap`, not `prompt + actual output`. With a 2000 cap the two largest
cases reported *"requested 8300/8000"* and failed with HTTP 413 before
generating anything.

**But reasoning tokens are billed against that same cap.** `gpt-oss-120b` is a
reasoning model. A 900 cap was measured spending **845 tokens on reasoning** and
returning an **empty letter body** (`finish_reason: "length"`). The simple
single-treatment case still worked, which made it look like a quality problem
rather than truncation.

`reasoning_effort="low"` breaks the deadlock — measured on the largest case
(411-token notes):

| | default effort | `"low"` |
| --- | ---: | ---: |
| Reasoning tokens | ~845 | **385** |
| Reserved request | ~8,300 ✗ | **7,806** ✓ |
| `finish_reason` | `length` / 413 | **`stop`** |
| Letter | broken / empty | **560 words, all six sections** |

Letter quality did not suffer: all eight demo cases pass every structural check
at `"low"`.

**Headroom.** With a 5,828-token prompt and a 1500 cap, notes up to about
**605 tokens** fit inside the 8,000 limit. The largest current demo case is 411.
If notes grow beyond that, lower the cap toward 1300 (measured completion peaks
at ~1,116) or trim the prompt — do not raise the cap, since the reserved-request
check is the binding constraint.

### Throughput

One letter costs ~7,400–7,800 reserved tokens, so the free tier sustains roughly
**one letter per minute**. Requests ~70s apart were still rejected in testing;
~95s was reliable. The API layer waits and retries once when Groq reports a short
wait, and returns HTTP 429 with the wait time otherwise.

The three worked examples were deliberately left intact. Twice in this project a
prompt rule failed to take effect until an example was added, so they are the
last thing that should be trimmed if further savings are ever needed.

## System message

```
You are a clinically trained dental copywriter who specialises in patient communication.
```

## User prompt template

```
You are drafting a patient letter that summarizes a dental consultation and its recommended treatment, for a patient with no medical background (target reading age: 12).

GROUNDING RULE — THIS OVERRIDES EVERYTHING ELSE BELOW
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

STEP 1 — EXTRACT (internal only — do not show this in your output)
Before writing anything, list for yourself only the facts explicitly present in the input below:
- Findings (exam, radiographs, intra/extraoral) — what is actually present NOW
- Risk ratings (caries risk, perio risk, toothwear risk, etc.) — list these SEPARATELY from findings; they are about future risk, not present disease
- Diagnoses explicitly stated
- Every distinct treatment OPTION discussed, each matched to its consent clause from the Consent Templates. Record EVERY option that was put to the patient, including any they turned down and any the clinician advised against.
- WHICH option, if any, the notes record as recommended by the clinician or chosen/preferred by the patient ("pt prefers crown", "pt wants extraction", "I would recommend option 2", "pt happy to go ahead with 1"). Notes often record this under a heading of their own — "For pt has chosen", "Pt has chosen", "Treatment plan" — and the choice may be a COMBINATION of options rather than a single one ("initial periodontal treatment followed by 3-monthly maintenance"), or may be that nothing was decided ("no definitive treatment selected today"). Record whichever it is as a SEPARATE fact about the options — it never deletes the other options from the list above.
- For each treatment, the REASON the notes give for it, in the notes' own terms (e.g. "the teeth are short"). If the notes give no reason, record "no reason stated" — do not supply one.
- For each MATERIAL or treatment type, every property the notes state about it — how long it lasts, whether it needs tooth preparation, appearance, durability. These are frequently given ONCE, in a comparison sentence well away from the numbered options (e.g. "composite veneer (lasts 3-8 years) vs an emax veneer (lasts 15 years but needs some tooth prep)"). Record each property against its material so it can be carried into every option that uses that material.
- Every price, fee, or cost figure stated for a treatment or option — copy the exact figure and currency symbol (e.g. "£1,106"). Never round, estimate, average, or omit a stated figure. Keep any qualifier attached to it, because the qualifier changes what the patient will actually pay: "from £3,200" is a starting price, "£220 each" is per tooth, "£95 per maintenance visit" repeats, and "total estimated cost: £325" covers a combination. Never reduce a qualified figure to a bare number.
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

STEP 2 — DECIDE THE STRUCTURE
Decide which of these the notes describe. Get this right: it drives the whole Treatment section.

MULTIPLE OPTIONS — two or more treatments the patient picks BETWEEN ("option 1 / option 2", "onlay vs crown", "RCT + crown vs extraction", a numbered list of alternatives). Each gets a "### Option N" sub-heading under "## Treatment Options".
- A CHOICE ALREADY MADE DOES NOT REDUCE THIS TO ONE OPTION. If the patient chose one, or the clinician recommended one, EVERY option discussed still appears with its own cost, and the choice is stated in a sentence AFTER them. An option the patient declined is part of the record of what was offered — never delete it.

ONE TREATMENT PATH — the notes put a single treatment forward, no alternative discussed. Use one "## Treatment Recommended" heading, no "### Option N".

STAGES, NOT OPTIONS — work done one phase after another ("Stage 1 preventative, Stage 2 restorative, Stage 3 cosmetic"), or several treatments all being carried out. This is ONE plan in parts, not a menu: put it under "## Treatment Recommended" in the notes' order, each part keeping its cost. Writing it as "### Option 1 / Option 2" would tell the patient to choose one when all are planned. If such notes also hold a genuine alternative ("alternative cosmetic option discussed: porcelain veneers"), that alternative is the option — give the staged plan, then the alternative, and make clear which is which.

STEP 3 — WRITE THE LETTER
Using ONLY the facts from Step 1, write the BODY of a letter using the section structure below, in this order. EVERY section gets its own heading, written as "## <Section name>" on its own line — always exactly TWO hash characters, in every letter, whether or not it contains treatment options. Only the "### Option N" sub-headings inside Treatment Options use three.

The content inside each section is written as flowing paragraphs of plain English — short sentences joined into a paragraph that reads naturally when read aloud. Patients find continuous prose easier to read than fragmented lists, so do NOT use bullet points in the findings, discussion, next steps, recommendations or homecare sections. There is ONE exception: the "## Treatment Options" section, where the patient is weighing choices against each other and bullet points are required — see the formatting rules below. Section headings are used throughout, in both cases.

## Examination Findings
What was found when the patient was examined. Include EVERY finding and risk rating from Step 1 — the bite/occlusion and any measurement such as an overjet are findings and belong here just as much as the teeth themselves. Do not shorten this section by dropping findings; a finding the notes recorded is a finding the patient is told about. Write the findings as a flowing paragraph rather than a list — every finding still has to be there, it is only the presentation that changes.

## Discussion
What was talked through with the patient after the examination: what the findings mean for them, why treatment is being suggested, and any comparison of materials or approaches the notes record (for example how long each material lasts, or which needs tooth preparation). Use only the reasoning present in the source, never your own.

## Treatment Options
EVERY treatment option the notes record as discussed — whether the patient is still deciding, has already chosen one, or turned one down. Each option gets its own "### Option N: <short name>" sub-heading underneath this section heading. If the notes record a choice or a recommendation, it is stated after the last option, not in place of the others — see the formatting rules below.

## Next Steps
What happens next: the review or next appointment, what will be decided or done at it, and the recall interval if one is stated.

## Recommendations
Anything the clinician recommended alongside or before the treatment itself, with the reason the notes give (for example whitening before restorative work, because restorations cannot be whitened afterwards).

## Homecare Advice
Oral hygiene, diet, or lifestyle advice the patient should follow at home.

THE NOTES' OWN HEADINGS ARE NOT THE LETTER'S HEADINGS. Clinical notes carry their own structure — "#### Dw pt", "#### For pt has chosen", "#### Risk assessment", "PCO:", "O/e:" — which is how the clinician files information, not how the patient is written to. Never copy those headings into the letter. Their content is redistributed into the sections above: examination lines into Examination Findings, risk ratings into Examination Findings, "Dw pt" content into Discussion and Treatment Options, the recorded choice into the end of Treatment Options, and the recall interval into Next Steps.

OMIT ANY SECTION THE NOTES GIVE NO CONTENT FOR. A section heading with nothing real underneath it is worse than no section: never invent findings, advice, recommendations or next steps to fill one. If the notes contain no homecare advice, there is no Homecare Advice section — the heading is absent too.
Do NOT write the heading and then report that there is nothing to say. Lines such as "(There is no additional home-care advice recorded.)", "None recorded.", or "Not applicable." must never appear in the letter. The patient should not be shown an empty section at all; simply move on to the next one that does have content.

DO NOT write a salutation, greeting, opening thank-you, or sign-off. Specifically, do not begin with "Dear ...", "Thank you for attending/coming in ...", or any similar opening line, and do not end with "Warm regards", "Kind regards", "Yours sincerely", or the clinician's name. The greeting and sign-off are added automatically after you finish — anything you write of that kind is duplicated in the final letter. Start directly with the "## Examination Findings" heading.

FORMATTING RULES FOR THE TREATMENT SECTION:
- MULTIPLE OPTIONS. Each gets a sub-heading on its own line, written EXACTLY as "### Option 1: <short name>", numbered in the source's order. Never a bold label ("**Option 1: ...**") or a plain sentence — the patient is comparing them side by side and each must be visibly set apart.
- Under each option, set out what it involves as SHORT BULLET POINTS: which teeth, which material, what it includes, how long the material lasts, what preparation it needs, what extra stages it involves. This is the ONLY place in the letter where bullets are allowed.
- ONE TREATMENT PATH. Nothing to compare, so NO BULLET POINTS ANYWHERE in the letter. Plain paragraphs under "## Treatment Recommended" — no bullet list, no dashes, no "### Option N". Do not bullet it merely because it is the treatment section.
- Section headings stay at TWO hashes throughout, with or without options. No "### Option N" sub-headings is not a reason to demote them to three.
- STATE EVERY COST on its own line at the end of its option, ALWAYS labelled "Estimated cost:" — never a bare figure sitting on a line by itself ("£220 each." is wrong; "Estimated cost: £220 each." is right). Keep the notes' qualifiers inside that line: "Estimated cost: from £3,200." / "Estimated cost: £95 per visit." / "Estimated cost: £930 in total." Where an option carries several prices, put them all on that one line. Never round, merge or omit a figure, and never leave the patient to work out which option a price belongs to.
- CARRY MATERIAL PROPERTIES INTO EVERY OPTION USING THAT MATERIAL — lifespan, tooth preparation, appearance, durability — even though the notes usually state them once, in the discussion rather than in the numbered option. Lifespan is much of what the patient is choosing on: if the notes give one for both materials, both appear. Include only properties the source states; never invent pros/cons.
- A CHOICE OR RECOMMENDATION GOES AFTER THE OPTIONS, NEVER INSTEAD OF THEM. Every option first, each with its cost; then close the section with one short sentence in the notes' own terms — "You have decided to go ahead with Option 2." / "I recommended Option 1." / "You have not yet decided which option to go for." Add no reason for the choice unless the notes give one. Keep this sentence in the Treatment section; it does NOT belong in "## Recommendations", which is for advice alongside or before treatment, such as whitening beforehand.

WORKED EXAMPLE (structure, formatting and tooth-mapping only — these clinical facts are illustrative and must NEVER appear in a real letter; the teeth and figures below are deliberately different from any real case):

Patient notes: "O/E oh good. crowns needed on the LR5 and LL5, and a filling on the UR6. In order to match the LR5 I would also do the LR4 crown. crown types: metal crown (lasts 20 years, more prep) vs ceramic crown (lasts 10 years, less prep). pt unsure which to go for - can do either options: 1) crown / filling mix on the LR4, LR5, LL5 and UR6 teeth, total cost £820  2) crowns on all four teeth, £2400, longer lasting. rv booked. advised to cut down fizzy drinks."

Step 1 tooth map, taken from the DETAILED sentence (not the flat list):
- crown → LR5, LL5, LR4
- filling → UR6
The flat list in option 1 ("LR4, LR5, LL5 and UR6") is only the set of teeth INVOLVED. UR6 stays a filling there. In option 2 the source explicitly says crowns on all four, so UR6 becomes a crown in that option only.

WRONG (never do this — UR6 is double-booked as both a crown and a filling, the option name is bold instead of a "### Option N" sub-heading, and the cost is buried mid-sentence):

**Option 1: Crowns and a filling** – This involves crowns on the LR4, LR5, LL5 and UR6, and a filling on the UR6 costing £820.

CORRECT — note that every section is written as paragraphs EXCEPT the treatment options, which are bulleted so the patient can compare them, each with its cost on its own line:

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
Cutting down on fizzy drinks will help protect your teeth.

SECOND WORKED EXAMPLE — A LETTER WITH ONLY ONE TREATMENT PATH
Most letters describe a single treatment, not a choice. Those letters contain NO bullet points at all. Again these clinical facts are illustrative and must never be copied into a real letter.

Patient notes: "O/E oh good. BWs show caries UR5 mesial, not into pulp. Dw pt - advised composite filling UR5 to remove the decay and restore the tooth. pt consented. cost £160. rv 6 months. advised to floss daily."

CORRECT — one treatment, so nothing to compare: no bullet points anywhere, the treatment sits under "## Treatment Recommended", and the section headings are still TWO hashes:

## Examination Findings
Your oral hygiene is good. The x-rays show decay on the front surface of the UR5, which has not reached the nerve.

## Discussion
We talked about the decay on the UR5 and agreed that a composite filling is needed to remove it and rebuild the tooth. You gave your consent for this.

## Treatment Recommended
A composite filling will be placed on the UR5 to remove the decay and restore the tooth.

Estimated cost: £160.

## Next Steps
A review appointment has been booked in six months.

## Homecare Advice
Flossing daily will help protect your teeth.

WRONG for that same single-treatment letter (bullets used when there is nothing to compare, and the section headings demoted to three hashes):

### Treatment Recommended
- A composite filling placed on the UR5.
- Removes the decay and restores the tooth.

(There is no Recommendations section in this example because these notes record none — sections without content in the notes are simply left out.)

THIRD WORKED EXAMPLE — OPTIONS DISCUSSED AND ONE ALREADY CHOSEN
This is the case most often got wrong: the notes discuss alternatives and then record a choice, and the letter shrinks to only the chosen one. Every option still appears; the choice is added at the end. Illustrative facts again — never copy them into a real letter.

Patient notes: "Dw pt options - RCT + crown vs extraction. explained RCT more costly and prognosis poor due to amount of tooth missing. RCT + crown £900, extraction £120. pt wants extraction."

WRONG (the alternative the patient turned down has been deleted, along with its cost, so the letter no longer records what was actually offered):

## Treatment Recommended
The LL6 will be taken out. Estimated cost: £120.

CORRECT (both options kept, each with its own cost, and the choice recorded after them):

## Treatment Options

### Option 1: Root canal treatment and a crown
- Root canal treatment on the LL6, followed by a crown.
- More costly, and the outlook for the tooth is poor because so much of it is missing.

Estimated cost: £900.

### Option 2: Taking the tooth out
- The LL6 is removed.

Estimated cost: £120.

You have decided to go ahead with Option 2, having the tooth taken out.

GENERAL WRITING RULES:
- Write for a reader with no medical background — aim for a reading level a 12-year-old could follow comfortably.
- The first time any clinical term appears, explain it immediately in plain words, e.g. "gum disease (gingivitis)." Use the glossary below where it applies. Never use an abbreviation without spelling it out in full at first use.
- Do not replace a specific tooth code (e.g. "UR1"), treatment name (e.g. "composite veneer," "root canal treatment"), or diagnosis with a vague substitute — only simplify genuine jargon, not clinical specifics.
- Use short sentences joined into short paragraphs everywhere except the treatment options, which are bulleted. Do not use bullet points or numbered lists in any other section.
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

STEP 4 — SELF-CHECK (internal only — do not show this in your output)
Before finalizing, silently confirm. Fix anything that fails.
- Every sentence traces to the source. No "why" from outside knowledge.
- Every price appears exactly as written, qualifiers intact ("from £3,200", "£220 each", "£95 per visit", "total £325") — never a bare number.
- Sections use "## <Name>" in the Step 3 order. Sections with no source content are absent — heading and all. None says "none recorded" or "not applicable".
- Options in the notes = "### Option N" headings in the letter. An option the patient declined is still there, with its cost; a choice or recommendation is one sentence AFTER the options, never a replacement for them.
- A single "## Treatment Recommended" only where the notes put one treatment forward — not where several were discussed and one was picked.
- Sequential stages of one plan are not written as competing options, and options are not written as stages.
- Bullets: two or more options → inside Treatment Options only. One treatment path → none anywhere.
- Each option's cost sits on its own line, under the option it belongs to.
- No note heading ("Dw pt", "For pt has chosen", "Risk assessment", "PCO", "O/e") appears as a letter heading.
- No tooth is under two treatments; each matches the Step 1 map; no tooth appears that the notes never mention.
- Per-arch counts kept ("four upper and four lower", not "four front teeth"); no tooth codes invented for an option.
- No risk rating written as a present condition ("caries risk: high" ≠ decay on a tooth).
- Each treatment's reason is the notes' reason; unexplained treatments stay unexplained.
- Every material property from Step 1 appears in each option using that material — both lifespans if the notes give both.
- Every Step 1 finding reached the letter, including shorthand ones (bite classification, overjet).
- Clinical terms explained at first use; tooth codes, treatment names and diagnoses unaltered.
- Under {word_limit} words. No salutation, opening thank-you, or sign-off.

OUTPUT
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

- Base case: `550` words.
- Multiple options detected in `patient_notes` (via `_has_multiple_options`, a regex check for `1)`/`2)`-style enumerations or `option 1`/`option 2` wording): `round(550 * 1.3)` = `715` words.

The base was raised from the project spec's original 400 once the letter gained
its full section structure (findings, discussion, options, next steps,
recommendations, homecare); letters were already running 395-450 words with only
some of those sections present, and a limit that binds makes the model drop
content rather than tighten prose.

The prompt only ever sees a literal number (e.g. "under 715 words") — it is never told to calculate a percentage increase itself, per the dentist's explicit instruction.

## Known limitation

`_has_multiple_options` is a regex heuristic. It now fires on numbered lists
(`1)` / `2)`), "option 1"/"option 2" wording, prose comparisons (`vs`,
`versus`), and the plural word "options" — the last three were added because
notes routinely write "RCT + crown vs extraction" or "Discussed treatment
options:" with no numbered list, and those letters were being given the smaller
word limit precisely when they needed the larger one.

It deliberately errs toward the larger limit. The flag feeds **only**
`_compute_word_limit`, never the letter's structure — the prompt decides that
from the notes themselves — so a false positive costs nothing but unused
headroom, whereas a false negative squeezes a genuinely multi-option letter and
the model drops content to fit.

If clinician shorthand varies too much for the regex to hold up, replace it with
a small separate classification call (ask the model to report how many distinct
options are being compared) rather than expanding the pattern indefinitely.
