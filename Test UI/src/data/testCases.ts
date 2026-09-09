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
        'MH no chnages\n\nPCO: just here for routine check up\n\nO/e: OH good. mild plaque lower anteriors. soft tissues healthy. cancer screen clear. no obvious caries. BPE 1-1-1/1-1-1\n\nDw pt\n\nadvised cont brushing 2x daily + interdental cleaning. no active treatment required at present.\n\n1) routine examination + OHI - £65\n\npt happy, no concerns. rv 6/12.\n\n#### Risk assessment\n- Caries risk: low\n- Perio risk: low\n- Toothwear risk: low\n- Recall: 6/12',
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
        'MH no changes\n\nPCO: sensitivity LL side esp cold drinks\n\nO/e: UR4 mesial caries, LL6 occlusal caries. both moderate depth. no pain on biting. no swelling.\n\nBWs taken - caries close to pulp but no obvious pulpal involvement.\n\nDw pt\n\nexplained both teeth need restorations. discussed filling options:\n\n1) composite filling UR4 + LL6 - £420 total. white fillings, good aesthetic result. may have some sensitivity after treatment.\n\n2) amalgam filling UR4 + LL6 - £300 total. stronger option for posterior teeth but silver appearance.\n\npt prefers white fillings. advised small chance of post op sensitivity and if nerve becomes irritated may require further treatment.\n\npt happy to proceed with composite. appt booked under LA.',
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
        'MH no changes\n\nPCO: gums bleeding when brushing, bad taste sometimes\n\nO/e: OH poor, generalised plaque + calculus, BOP. BPE 2-2-2/2-2-3. LR6/7 pockets 5-6mm. xray shows horizontal bone loss.\n\nDw pt\n\nexplained signs of gum disease + need to improve OH. discussed treatment options.\n\n1) routine hygiene treatment + OHI - £120 per visit. suitable for improving plaque/calculus and home care.\n\n2) periodontal treatment / root surface debridement - £450 over 2 visits. needed for deeper pockets and deposits below gum level.\n\npt understands. wants to go ahead with perio treatment. interdental brushes shown.\n\nreview 3 months after treatment to reassess pockets.',
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
        'MH no changes\n\nPCO: pain LL6 for few days, worse chewing\n\nO/e: LL6 grossly carious + broken down below gum. tender to bite. no facial swelling.\n\nxray shows large PA lesion. tooth not restorable.\n\nDw pt\n\nexplained options for LL6:\n\n1) RCT + crown - approx £2200. would try to save tooth but prognosis guarded due to amount of tooth missing.\n\n2) extraction - £180. remove tooth, simpler + lower cost. replacement can be considered later.\n\npt chose extraction due to cost + poor prognosis of tooth. risks explained inc pain, swelling, bruising + dry socket.\n\nwritten consent obtained. extraction next visit under LA.\n\nreplacement options later could include bridge / denture / implant.',
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
        'MH no changes\n\nPCO: UL6 sharp pain on biting on/off\n\nO/e: large old amalgam UL6, cracked cusp. pulp test WNL. no swelling. limited tooth structure remaining.\n\nDw pt\n\nexplained tooth needs cuspal protection. discussed 2 options.\n\n1) onlay - £850. more conservative, less tooth prep but may not fully protect tooth depending on crack.\n\n2) full crown - £1100. more tooth prep but gives better overall protection + more predictable long term result.\n\nexplained if crack progresses may need RCT or extraction. pt prefers crown.\n\npt consented. prep + temporary crown planned. permanent crown fit approx 2-3 weeks.',
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
        'MH no changes\n\nPCO: wants teeth checked, also jaw ache in morning\n\nO/e: UR5 distal caries + LR7 occlusal caries. both restorable. BPE 2-2-1/1-2-2. plaque + mild gingivitis. masseter mildly TTP, no TMJ click. signs of tooth wear consistent with bruxism.\n\nDw pt\n\nadvised composite fillings for UR5 + LR7, hygiene treatment + nightguard due to grinding.\n\n1) fillings only UR5 + LR7 - £420\n\n2) fillings + scale/OHI - £540\n\n3) full plan incl fillings, hygiene + nightguard - £890\n\nexplained nightguard helps protect teeth from further wear and may reduce muscle strain. pt wants full plan and agrees to treatment over 3 visits.\n\nappt booked.',
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
        'PCO broken tooth LR6\n\nO/e small cavity\n\nDw pt - composite filling advised £180\n\npt happy to proceed. appt booked.',
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
        'MH no changes\n\nPCO acute pain UL7\n\nO/e: chronic gingivitis + localised perio UL6/7. UL7 distal caries, vitality WNL. PA shows possible periapical pathology / perio-endo lesion. no trismus. TMJ mild discomfort, masseter + temporalis TTP bilat. Class III incisor relationship stable.\n\nDw pt\n\nexplained UL7 requires restoration and gum treatment needed around UL6/7. discussed options:\n\n1) composite UL7 + perio debridement - £650\n\n2) composite UL7 + routine hygiene treatment - £500, with reassessment of perio areas\n\npt prefers option 1. advised UL7 perio-endo status will need monitoring and further treatment may be required depending on symptoms/radiographic changes. TMJ symptoms to be reviewed next visit.\n\npt consented. review booked.',
    },
  },
]