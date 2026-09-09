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
        'MH no changes\n\nroutine 6 monthly check\n\nO/e: OH good, little plaque lower anteriors. soft tissues all NAD. oral cancer screen clear. no obvious caries. BPE 1-1-1/1-1-1\n\nDw pt\n\nadvised continue brushing 2x daily with fluoride toothpaste + interdental cleaning. no treatment needed. rv 6/12',
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
        'MH no changes\n\nPCO sensitivity LL side esp cold\n\nBWs taken - caries UR4 mesial + LL6 occlusal, moderate depth but not into pulp.\n\nDw pt - fillings needed. discussed composite vs amalgam, pt would prefer white filling. explained poss post op sensitivity + small chance nerve may become irritated and need RCT later.\n\n1) composite fillings UR4 + LL6 - £420 total\n\npt happy to go ahead next visit LA required. consented.',
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
        'MH no changes\n\nOH not great. bleeding when brushing.\n\nO/e generalised plaque + calculus, BOP. BPE 2-2-2/2-2-3. LR6/7 pockets 5-6mm. xray shows horizontal bone loss. perio discussed.\n\nDw pt - needs perio treatment + improve home care. advised scale and root surface debridement over 2 visits.\n\n1) perio treatment in practice £450\n\npt agrees. interdental brushes shown + advised daily. review 3 months to check response.',
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
        'MH no changes\n\npt attended in pain LL6\n\nO/e LL6 grossly carious, tooth broken down below gum. xray shows large PA lesion. tooth not restorable.\n\nDw pt options - RCT + crown vs extraction. explained RCT would be more costly and prognosis poor due to amount of tooth missing.\n\npt wants extraction.\n\nrisks explained inc pain/swelling, bruising, dry socket. replacement options can be discussed later - bridge / denture / implant.\n\nextraction planned next visit under LA. consent obtained.',
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
        'MH no changes\n\nPCO UL6 sharp pain on biting on/off\n\nO/e large old amalgam UL6, cracked cusp. pulp tests WNL. no swelling. tooth has limited remaining structure.\n\nDw pt - tooth needs cuspal protection. discussed onlay vs crown. if crack extends may need RCT or extraction.\n\n1) onlay - less prep but may not give enough protection depending on crack\n2) full crown - more predictable protection, requires more prep\n\npt prefers crown.\n\nimpressions taken + temp crown planned. permanent crown fit approx 2-3 weeks.',
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
        'MH no changes\n\ncomprehensive exam. UR5 distal + LR7 occlusal caries. both look restorable with composite.\n\nBPE 2-2-1/1-2-2, plaque + mild gum inflammation. scale/clean needed. pt also reports jaw ache in morning, likely grinding. masseter slightly tender, no clicking.\n\nDw pt\n\nadvised fillings UR5 + LR7, hygiene treatment + nightguard for bruxism. explained nightguard will help protect teeth from further wear.\n\npt happy with plan, wants to do over 3 visits.\n\nTreatment: composite UR5, composite LR7, scale + polish/OHI, nightguard. rv as booked.',
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
        'LR6 cavity. filling needed. pt happy to proceed. composite filling next visit.',
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
        'MH no changes\n\nPCO acute pain UL7\n\nO/e chronic gingivitis + localised perio UL6/7. UL7 carious distally, vitality WNL. PA shows possible periapical pathology / perio-endo lesion. no trismus. TMJ mild discomfort, masseter + temporalis TTP bilat.\n\nClass III incisor relationship, stable.\n\nDw pt - UL7 needs restoration. perio debridement advised. monitor UL7 perio-endo changes + review TMJ.\n\n1) composite UL7 + perio debridement\n\npt agrees. review TMJ + UL7 at next visit.',
    },
  },
]