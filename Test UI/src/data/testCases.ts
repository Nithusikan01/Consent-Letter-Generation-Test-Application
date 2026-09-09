import type { TestCase } from '../types'

// All patient names, clinicians and notes below are fictional demo data only.

export const testCases: TestCase[] = [
  {
    id: 'routine-examination',
    label: '1. Routine examination',
    description: 'A standard check-up with no significant findings.',
    values: {
      patientName: 'Jane Doe',
      clinicianName: 'Dr. Priya Shah',
      patientNotes:
        'MH no changes\n\nPCO: attended for routine examination. No specific concerns.\n\nO/e: OH fair. No pain or sensitivity reported. Existing restorations satisfactory. No obvious cavitated lesions. Gingivae generally healthy with mild localised inflammation around lower anterior teeth.\n\nBPE: 1 1 1 / 1 1 1\n\n#### Dw pt\n\nDiscussed findings with patient. Advised that there are no urgent treatment needs at present. Recommended continuing twice daily brushing with fluoride toothpaste and interdental cleaning.\n\nAdvised routine examination and hygiene maintenance.\n\nHygienist appointment: £75\nRoutine examination: £65\n\nPt happy to continue with preventative care.\n\n#### For pt has chosen\n\nRoutine examination + hygiene appointment.\n\n#### Risk assessment\n\n- Caries risk: low\n- Perio risk: low\n- Toothwear risk: low\n- Recall: 12 months',
    },
  },

  {
    id: 'caries-fillings',
    label: '2. Caries / fillings',
    description: 'Two carious lesions requiring composite fillings.',
    values: {
      patientName: 'Tom Baker',
      clinicianName: 'Dr. Michael Turner',
      patientNotes:
        'MH no changes\n\nPCO: concerned about sensitivity from the lower left back tooth, particularly when eating cold foods.\n\nO/e: OH fair. LL6 has an existing large occlusal restoration with recurrent caries at the distal margin. LL7 has early fissure caries. No swelling or sinus noted.\n\nPA radiograph taken. Caries associated with LL6 restoration extending towards the dentine but no obvious periapical pathology.\n\n#### Dw pt\n\nExplained that the LL6 filling is leaking and there is decay underneath the existing restoration.\n\nDiscussed treatment options:\n\n1) Remove existing restoration and replace with a composite filling - £180.\n\n2) If insufficient tooth structure remains after removing the decay, a larger indirect restoration may be required. Estimated cost for an onlay: £650.\n\n3) LL7 can be monitored or restored with a small composite filling. Composite filling cost: £145.\n\nPt would like to proceed conservatively with fillings initially.\n\nAdvised that if LL6 symptoms worsen or the tooth becomes painful, further treatment including root canal treatment may be required.\n\n#### For pt has chosen\n\nLL6 composite restoration and LL7 composite restoration.\n\nTotal estimated cost: £325.\n\n#### Risk assessment\n\n- Caries risk: medium\n- Perio risk: low\n- Toothwear risk: low\n- Recall: 6 months',
    },
  },

  {
    id: 'periodontal-treatment',
    label: '3. Periodontal treatment',
    description: 'Moderate gum disease requiring periodontal therapy.',
    values: {
      patientName: 'Amara Okafor',
      clinicianName: 'Dr. Sarah Lindqvist',
      patientNotes:
        'MH no changes\n\nPCO: bleeding gums when brushing and occasional bad taste.\n\nO/e: OH poor. Generalised plaque and calculus deposits, particularly lower anterior region. Generalised gingival inflammation with bleeding on probing.\n\nBPE: 3 3 2 / 3 3 2\n\n6-point pocket chart completed. Generalised periodontal pocketing of 4-5mm with isolated 6mm sites around LL6 and LR6.\n\n#### Dw pt\n\nExplained that the gum inflammation is associated with plaque and calculus and that there are signs of periodontal disease.\n\nRecommended initial periodontal treatment consisting of oral hygiene instruction and subgingival instrumentation.\n\n1) Standard hygiene appointment and oral hygiene instruction - £95.\n\n2) Full periodontal treatment with multiple appointments, including local anaesthetic where required - £420.\n\n3) Periodontal treatment followed by regular 3-month maintenance visits - £95 per maintenance visit.\n\nExplained that periodontal treatment aims to control the disease but cannot restore lost bone.\n\nPt would like to proceed with periodontal treatment.\n\nInterdental brushes demonstrated and oral hygiene advice provided.\n\n#### For pt has chosen\n\nInitial periodontal treatment followed by 3-monthly maintenance.\n\nInitial treatment: £420\nMaintenance: £95 per visit.\n\n#### Risk assessment\n\n- Caries risk: medium\n- Perio risk: high\n- Toothwear risk: low\n- Recall: 3 months',
    },
  },

  {
    id: 'extraction',
    label: '4. Extraction',
    description: 'A non-restorable tooth requiring extraction.',
    values: {
      patientName: 'Liam Chen',
      clinicianName: 'Dr. Michael Turner',
      patientNotes:
        'MH no changes\n\nPCO: pain from UL6 for approximately one week. Pain worse when chewing.\n\nO/e: UL6 heavily restored with extensive fracture and tenderness to percussion. Tooth has poor remaining tooth structure. No facial swelling. Localised gingival inflammation.\n\nRadiograph shows extensive structural loss associated with UL6. Prognosis considered poor.\n\n#### Dw pt\n\nExplained that UL6 is extensively compromised and is unlikely to be predictably restored.\n\nDiscussed options:\n\n1) Extraction of UL6 - £150.\n\n2) Attempt to retain the tooth with root canal treatment followed by crown treatment. Estimated total cost: £1,250.\n\n3) Extraction followed by replacement with an implant-supported crown. Estimated cost from £3,200.\n\nAdvised that extraction would resolve the immediate problem but would leave a missing tooth. Replacement is optional depending on function and aesthetics.\n\nPt would like to have the tooth extracted.\n\nExtraction appointment booked.\n\n#### For pt has chosen\n\nUL6 extraction.\n\nEstimated cost: £150.\n\n#### Risk assessment\n\n- Caries risk: high\n- Perio risk: medium\n- Toothwear risk: low\n- Recall: 6 months',
    },
  },

  {
    id: 'crown-treatment',
    label: '5. Crown treatment',
    description: 'A heavily restored tooth needing a crown.',
    values: {
      patientName: 'Grace Bennett',
      clinicianName: 'Dr. Priya Shah',
      patientNotes:
        'MH no changes\n\nPCO: unhappy with appearance of heavily filled UR1 and occasional sensitivity.\n\nO/e: UR1 has extensive existing composite restoration with marginal staining and reduced remaining tooth structure. Tooth currently asymptomatic. No swelling or sinus.\n\nRadiograph satisfactory with no obvious periapical pathology.\n\n#### Dw pt\n\nDiscussed that the existing restoration could be replaced, although due to the amount of tooth structure missing a crown may provide a more predictable long-term restoration.\n\nTreatment options discussed:\n\n1) Replace existing composite restoration - £250.\n\n2) Porcelain crown - £950.\n\n3) Emax crown - £1,050.\n\nExplained that crown treatment requires preparation of the tooth and that the final shade and shape can be selected before the definitive crown is fitted.\n\nPt would like the Emax crown for the most aesthetic result.\n\nA temporary crown will be provided while the definitive crown is fabricated.\n\n#### For pt has chosen\n\nEmax crown UR1 - £1,050.\n\nPt understands that the tooth will require preparation and that the treatment is irreversible.\n\n#### Risk assessment\n\n- Caries risk: medium\n- Perio risk: low\n- Toothwear risk: low\n- Recall: 6 months',
    },
  },

  {
    id: 'multiple-treatments',
    label: '6. Multiple treatments',
    description: 'A combined treatment plan across several issues.',
    values: {
      patientName: 'Olusegun Adeyemi',
      clinicianName: 'Dr. Sarah Lindqvist',
      patientNotes:
        'MH no changes\n\nPCO: wants to improve general dental health and is also concerned about the appearance of the upper front teeth.\n\nO/e: OH fair. Moderate calculus deposits. UR1 and UL1 have old composite restorations with staining. LL6 has recurrent caries beneath an existing restoration. LR6 has fractured cusp with a large existing restoration. Mild lower anterior crowding.\n\n#### Dw pt\n\nDiscussed findings and explained that treatment would ideally be completed in stages.\n\nStage 1 - Preventative care:\n- Hygiene treatment - £90\n- Oral hygiene instruction included.\n\nStage 2 - Restorative treatment:\n- LL6 composite restoration - £190\n- LR6 onlay - £650\n\nStage 3 - Cosmetic treatment:\n- Replacement composite restorations on UR1 and UL1 - £220 each.\n- Composite bonding of lower anterior teeth - £650.\n\nAlternative cosmetic option discussed:\n\nPorcelain veneers for UR1 and UL1 - £1,900 for two teeth.\n\nExplained that cosmetic treatment should be undertaken after stabilising oral health.\n\n#### For pt has chosen\n\nPt would like to begin with hygiene and restorative treatment before deciding on cosmetic treatment.\n\nInitial planned treatment:\n\nHygiene: £90\nLL6 filling: £190\nLR6 onlay: £650\n\nTotal initial phase: £930.\n\nCosmetic options to be reviewed once restorative treatment is complete.\n\n#### Risk assessment\n\n- Caries risk: high\n- Perio risk: medium\n- Toothwear risk: medium\n- Recall: 6 months',
    },
  },

  {
    id: 'minimal-notes',
    label: '7. Minimal clinical notes',
    description: 'Very brief notes to test handling of sparse input.',
    values: {
      patientName: 'Ella Robertson',
      clinicianName: 'Dr. Michael Turner',
      patientNotes:
        'PCO broken tooth LR6\n\nO/e small cavity\n\nDw pt - composite filling advised - £180\n\nPt happy to proceed. Appt booked.',
    },
  },

  {
    id: 'clinical-terminology',
    label: '8. Notes containing clinical terminology',
    description: 'Jargon-heavy notes to test plain-English translation.',
    values: {
      patientName: 'Nadia Petrova',
      clinicianName: 'Dr. Sarah Lindqvist',
      patientNotes:
        'MH no changes\n\nPCO: intermittent discomfort from LR7 and concerned about generalised toothwear.\n\nO/e: OH fair. Generalised mild gingival inflammation. LR7 tender to percussion with a large occlusal amalgam restoration and suspected recurrent caries at the distal margin. No sinus tract or swelling.\n\nLR6 demonstrates moderate occlusal wear with loss of cuspal anatomy. Generalised mild-to-moderate erosive toothwear affecting the posterior dentition. Localised recession noted around LL3.\n\nBPE: 2 2 2 / 2 3 2\n\n6-point pocket chart completed around affected teeth.\n\nPA of LR7 taken. Radiographic evidence of caries approaching the pulp, with no definite periapical radiolucency.\n\n#### Dw pt\n\nDiscussed the clinical and radiographic findings.\n\nExplained that the LR7 restoration is compromised and recurrent caries is present. The depth of the lesion means there is a risk of pulpal involvement during removal of the caries.\n\nTreatment options:\n\n1) Remove existing restoration and restore LR7 with composite - £220. Explained that this is the most conservative option but carries a risk of pulpal symptoms.\n\n2) Root canal treatment followed by cuspal coverage - approximately £1,350.\n\n3) Extraction of LR7 - £150, with replacement options to be discussed separately.\n\nRegarding the toothwear, explained that the current wear pattern may be multifactorial, including attrition and erosion. Recommended monitoring and preventative measures before considering extensive restorative treatment.\n\nDiscussed use of high-fluoride toothpaste where appropriate, reducing frequency of acidic drinks and avoiding aggressive brushing.\n\nPt unsure whether to proceed with restoration or extraction and would like time to consider.\n\n#### For pt has chosen\n\nNo definitive treatment selected today.\n\nPt would like to review options at next appointment.\n\nReview appointment: £65.\n\n#### Risk assessment\n\n- Caries risk: high\n- Perio risk: medium\n- Toothwear risk: high\n- Recall: 6 months',
    },
  },
]

