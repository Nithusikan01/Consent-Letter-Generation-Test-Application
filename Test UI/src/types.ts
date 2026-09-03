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

export type YesNoSomewhat = 'yes' | 'somewhat' | 'no' | ''
export type YesNo = 'yes' | 'no' | ''

export interface FeedbackData {
  overallRating: number | null
  languageEasy: YesNoSomewhat
  accurateToNotes: YesNoSomewhat
  missingImportant: YesNo
  missingDetail: string
  unnecessaryOrIncorrect: YesNo
  unnecessaryDetail: string
  comments: string
}

export const emptyFeedback: FeedbackData = {
  overallRating: null,
  languageEasy: '',
  accurateToNotes: '',
  missingImportant: '',
  missingDetail: '',
  unnecessaryOrIncorrect: '',
  unnecessaryDetail: '',
  comments: '',
}

export const emptyFormValues: LetterFormValues = {
  patientName: '',
  clinicianName: '',
  treatmentPlanItems: '',
  patientNotes: '',
}
