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
        'Routine 6-monthly dental examination. Extraoral and intraoral soft tissue exam unremarkable, oral cancer screening clear. Oral hygiene good, mild plaque on lower incisors. No caries detected on visual and radiographic exam. BPE 1-1-1/1-1-1. Advised to continue twice daily brushing with fluoride toothpaste and interdental cleaning. Recall in 6 months. Treatment plan: routine examination, oral hygiene advice.',
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
        'Patient presents with sensitivity to cold on the lower left. Bitewing radiographs show moderate carious lesions on UR4 (mesial) and LL6 (occlusal), both close to but not involving the pulp. Discussed composite vs amalgam restoration, patient opted for composite (white) fillings on both teeth. Explained possible post-operative sensitivity and small risk of requiring root canal treatment if the nerve becomes irritated. Consented for treatment, to be completed next visit under local anaesthetic. Treatment plan: composite filling UR4, composite filling LL6.',
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
        'BPE 2-2-2/2-2-3. Generalised moderate plaque and calculus with bleeding on probing. Localised 5-6mm pockets on LR6 and LR7 with clinical attachment loss, radiographs confirm horizontal bone loss consistent with periodontitis. Diagnosis: generalised chronic periodontitis, localised severe on lower right molars. Discussed non-surgical periodontal treatment (scale and root surface debridement) over two visits, alternative of referral to a specialist hygienist explained. Patient agrees to in-practice treatment. Advised on interdental brushing technique, review in 3 months to reassess pocket depths. Treatment plan: periodontal scale and clean, oral hygiene instruction, 3 month recall.',
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
        'Patient attended in pain, LL6 grossly carious with a large periapical radiolucency on radiograph consistent with a chronic dental abscess. Tooth deemed unrestorable due to extent of decay below the gum line. Discussed options: root canal treatment plus crown versus extraction. Patient elects extraction due to cost and poor long term prognosis. Risks explained including swelling, bruising, dry socket and the need to consider replacement (bridge, denture or implant) in future. Written consent obtained, extraction planned for next appointment under local anaesthetic. Treatment plan: extraction LL6.',
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
        'UL6 has a large existing amalgam restoration with a cracked cusp, patient reports intermittent sharp pain on biting. Cracked tooth syndrome suspected. Pulp testing within normal limits. Insufficient healthy tooth remaining (ferrule) to support a further filling. Discussed crown as the most predictable long-term option to protect the tooth, versus onlay or, if the crack extends further, possible root canal treatment or extraction later. Patient consents to full coverage crown. Impressions and temporary crown to be provided this visit, permanent crown fitted in 2-3 weeks. Treatment plan: crown preparation UL6, temporary crown, fit permanent crown.',
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
        'Comprehensive exam. Two new carious lesions identified: UR5 (distal, moderate) and LR7 (occlusal, moderate), both suitable for composite fillings. BPE 2-2-1/1-2-2 with mild to moderate gum inflammation, scale and clean recommended alongside improved interdental cleaning. Patient also reports morning jaw ache and tooth wear consistent with nocturnal bruxism (tooth grinding); facial muscles mildly tender to palpation, no clicking of the jaw joint. Discussed a nightguard to protect the teeth and reduce muscle strain. All findings and options discussed, patient consents to full plan to be completed over three visits. Treatment plan: composite filling UR5, composite filling LR7, periodontal scale and clean, oral hygiene instruction, nightguard for bruxism.',
    },
  },
  {
    id: 'minimal-notes',
    label: '7. Minimal clinical notes',
    description: 'Very brief notes to test handling of sparse input.',
    values: {
      patientName: 'Ella Robertson',
      clinicianName: 'Dr. Michael Turner',
      patientNotes: 'Small cavity LR6. Filling needed. Patient happy to proceed. Treatment plan: composite filling LR6.',
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
        'Pt c/o acute pain UL7, chronic gingivitis noted generally with localised periodontitis UL6-UL7. Periapical pathology suspected UL7 on PA radiograph, possible perio-endo lesion, will monitor and review need for endodontic referral. Carious lesion UL7 distal, pulp vitality WNL currently. Also reports mild TMJ discomfort, temporalis and masseter tender to palpation bilaterally, no trismus. Class III incisal relationship noted, stable, no active treatment indicated. Plan: composite restoration UL7, periodontal debridement, monitor perio-endo status, review TMJ symptoms at next visit. Treatment plan: periodontal scale and clean, composite filling UL7, review TMJ symptoms.',
    },
  },
]
