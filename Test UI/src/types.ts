export interface LetterFormValues {
  patientName: string
  clinicianName: string
  treatmentPlanItems: string
  patientNotes: string
}

export interface GenerateLetterRequest {
  patient_name: string
  clinician_name: string
  treatment_plan_items: string[]
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
  treatmentPlanItems: '',
  patientNotes: '',
}
