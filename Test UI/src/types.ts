export interface LetterFormValues {
  patientName: string
  clinicianName: string
  patientNotes: string
}

export interface GenerateLetterRequest {
  patient_name: string
  clinician_name: string
  patient_notes: string
}

export interface GenerateLetterResponse {
  html: string
  full_letter: string
  style?: LetterStyleId
}

/** Letter styles. Identical clinically — only the presentation differs. */
export type LetterStyleId = 'standard' | 'bulleted' | 'narrative'

export interface LetterStyleOption {
  id: LetterStyleId
  label: string
  description: string
  endpoint: string
  recommended?: boolean
}

export const letterStyles: LetterStyleOption[] = [
  {
    id: 'standard',
    label: 'Standard',
    description:
      'Paragraphs throughout, with the treatment options set out as bullets so they can be compared.',
    endpoint: '/test/generate-patient-letter',
    recommended: true,
  },
  {
    id: 'bulleted',
    label: 'Bulleted',
    description: 'Bullet points used throughout, including the findings. For comparison only.',
    endpoint: '/test/generate-patient-letter-bulleted',
  },
  {
    id: 'narrative',
    label: 'Narrative',
    description: 'Flowing paragraphs everywhere, including the options. For comparison only.',
    endpoint: '/test/generate-patient-letter-narrative',
  },
]

export const defaultLetterStyle: LetterStyleId = 'standard'

export interface TestCase {
  id: string
  label: string
  description: string
  values: LetterFormValues
}

export const emptyFormValues: LetterFormValues = {
  patientName: '',
  clinicianName: '',
  patientNotes: '',
}
