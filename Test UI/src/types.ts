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
}

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
