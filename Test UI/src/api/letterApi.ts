import axios from 'axios'
import { apiClient } from './client'
import { defaultLetterStyle, letterStyles } from '../types'
import type {
  GenerateLetterRequest,
  GenerateLetterResponse,
  LetterFormValues,
  LetterStyleId,
} from '../types'

export function toGenerateRequest(values: LetterFormValues): GenerateLetterRequest {
  return {
    patient_name: values.patientName.trim(),
    clinician_name: values.clinicianName.trim(),
    patient_notes: values.patientNotes.trim(),
  }
}

/** Each style has its own endpoint; the request body is the same for both. */
function endpointFor(style: LetterStyleId): string {
  const match = letterStyles.find((s) => s.id === style)
  return (match ?? letterStyles.find((s) => s.id === defaultLetterStyle)!).endpoint
}

export async function generatePatientLetter(
  values: LetterFormValues,
  style: LetterStyleId = defaultLetterStyle,
): Promise<GenerateLetterResponse> {
  try {
    const { data } = await apiClient.post<GenerateLetterResponse>(
      endpointFor(style),
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
