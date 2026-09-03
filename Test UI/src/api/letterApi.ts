import axios from 'axios'
import { apiClient } from './client'
import type { FeedbackData, GenerateLetterRequest, GenerateLetterResponse, LetterFormValues } from '../types'

const GENERATE_LETTER_PATH = '/test/generate-patient-letter'

export function toGenerateRequest(values: LetterFormValues): GenerateLetterRequest {
  const treatmentPlanItems = values.treatmentPlanItems
    .split(/[,\n]/)
    .map((item) => item.trim())
    .filter(Boolean)

  return {
    patient_name: values.patientName.trim(),
    clinician_name: values.clinicianName.trim(),
    treatment_plan_items: treatmentPlanItems,
    patient_notes: values.patientNotes.trim(),
  }
}

export async function generatePatientLetter(
  values: LetterFormValues,
): Promise<GenerateLetterResponse> {
  try {
    const { data } = await apiClient.post<GenerateLetterResponse>(
      GENERATE_LETTER_PATH,
      toGenerateRequest(values),
    )
    return data
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = (err.response?.data as { detail?: string } | undefined)?.detail
      throw new Error(detail || err.message || 'Failed to generate the patient letter.')
    }
    throw err
  }
}

export interface FeedbackSubmission {
  feedback: FeedbackData
  formValues: LetterFormValues
  letterHtml: string
  submittedAt: string
}

/**
 * Placeholder for feedback submission. The backend has no feedback endpoint yet,
 * so this only logs and resolves locally. Swap the body for a real API call
 * (e.g. apiClient.post('/api/v2/test/feedback', submission)) once one exists.
 */
export async function submitFeedback(submission: FeedbackSubmission): Promise<void> {
  // eslint-disable-next-line no-console
  console.info('Feedback captured (stored locally only):', submission)
  return Promise.resolve()
}
