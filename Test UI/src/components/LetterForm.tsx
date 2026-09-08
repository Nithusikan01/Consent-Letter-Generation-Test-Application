import type { ChangeEvent } from 'react'
import { Box, Button, CircularProgress, Divider, Stack, TextField } from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import { LetterStyleSelector } from './LetterStyleSelector'
import type { LetterFormValues, LetterStyleId } from '../types'

interface LetterFormProps {
  values: LetterFormValues
  onChange: (values: LetterFormValues) => void
  onSubmit: () => void
  loading: boolean
  style: LetterStyleId
  onStyleChange: (style: LetterStyleId) => void
}

export function LetterForm({
  values,
  onChange,
  onSubmit,
  loading,
  style,
  onStyleChange,
}: LetterFormProps) {
  const isValid = values.patientName.trim() && values.clinicianName.trim() && values.patientNotes.trim()

  const setField = (field: keyof LetterFormValues) => (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange({ ...values, [field]: e.target.value })
  }

  return (
    <Box
      component="form"
      onSubmit={(e) => {
        e.preventDefault()
        if (isValid && !loading) onSubmit()
      }}
    >
      <Stack spacing={2}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            label="Patient Name"
            value={values.patientName}
            onChange={setField('patientName')}
            fullWidth
            required
            disabled={loading}
          />
          <TextField
            label="Clinician Name"
            value={values.clinicianName}
            onChange={setField('clinicianName')}
            fullWidth
            required
            disabled={loading}
          />
        </Stack>
        <TextField
          label="Patient Notes"
          value={values.patientNotes}
          onChange={setField('patientNotes')}
          helperText="The clinical notes the letter will be generated from, including the treatment plan. This is the only clinical input, matching the real app."
          fullWidth
          multiline
          minRows={10}
          required
          disabled={loading}
        />
        <Divider />
        <LetterStyleSelector value={style} onChange={onStyleChange} disabled={loading} />
        <Box>
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={!isValid || loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeIcon />}
          >
            {loading ? 'Generating letter…' : 'Generate Patient Letter'}
          </Button>
        </Box>
      </Stack>
    </Box>
  )
}
