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
export type LetterStyleId = 'bulleted' | 'narrative'

export interface LetterStyleOption {
  id: LetterStyleId
  label: string
  description: string
  endpoint: string
}

export const letterStyles: LetterStyleOption[] = [
  {
    id: 'bulleted',
    label: 'Bulleted',
    description: 'Findings and options broken into short bullet points for quick scanning.',
    endpoint: '/test/generate-patient-letter',
  },
  {
    id: 'narrative',
    label: 'Narrative',
    description: 'The same letter written as flowing paragraphs, with no bullet points.',
    endpoint: '/test/generate-patient-letter-narrative',
  },
]

export const defaultLetterStyle: LetterStyleId = 'bulleted'

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
