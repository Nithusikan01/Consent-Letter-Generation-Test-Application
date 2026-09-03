import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Rating,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import type { FeedbackData, YesNo, YesNoSomewhat } from '../types'
import { emptyFeedback } from '../types'

interface FeedbackFormProps {
  onSubmit: (feedback: FeedbackData) => Promise<void>
}

export function FeedbackForm({ onSubmit }: FeedbackFormProps) {
  const [feedback, setFeedback] = useState<FeedbackData>(emptyFeedback)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const set = <K extends keyof FeedbackData>(field: K, value: FeedbackData[K]) => {
    setFeedback((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      await onSubmit(feedback)
      setSubmitted(true)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <Alert
        severity="success"
        action={
          <Button
            color="inherit"
            size="small"
            onClick={() => {
              setFeedback(emptyFeedback)
              setSubmitted(false)
            }}
          >
            Edit feedback
          </Button>
        }
      >
        Thanks — your feedback has been recorded.
      </Alert>
    )
  }

  return (
    <Stack spacing={3}>
      <FormControl>
        <FormLabel>Overall rating</FormLabel>
        <Rating
          size="large"
          value={feedback.overallRating}
          onChange={(_, value) => set('overallRating', value)}
        />
      </FormControl>

      <YesNoSomewhatQuestion
        label="Is the language easy for a patient to understand?"
        value={feedback.languageEasy}
        onChange={(v) => set('languageEasy', v)}
      />

      <YesNoSomewhatQuestion
        label="Does the letter accurately represent the clinical notes?"
        value={feedback.accurateToNotes}
        onChange={(v) => set('accurateToNotes', v)}
      />

      <Box>
        <YesNoQuestion
          label="Is anything important missing?"
          value={feedback.missingImportant}
          onChange={(v) => set('missingImportant', v)}
        />
        {feedback.missingImportant === 'yes' && (
          <TextField
            label="What's missing?"
            value={feedback.missingDetail}
            onChange={(e) => set('missingDetail', e.target.value)}
            fullWidth
            multiline
            minRows={2}
            sx={{ mt: 1.5 }}
          />
        )}
      </Box>

      <Box>
        <YesNoQuestion
          label="Is anything unnecessary or incorrect?"
          value={feedback.unnecessaryOrIncorrect}
          onChange={(v) => set('unnecessaryOrIncorrect', v)}
        />
        {feedback.unnecessaryOrIncorrect === 'yes' && (
          <TextField
            label="What's unnecessary or incorrect?"
            value={feedback.unnecessaryDetail}
            onChange={(e) => set('unnecessaryDetail', e.target.value)}
            fullWidth
            multiline
            minRows={2}
            sx={{ mt: 1.5 }}
          />
        )}
      </Box>

      <TextField
        label="General comments / suggestions"
        value={feedback.comments}
        onChange={(e) => set('comments', e.target.value)}
        fullWidth
        multiline
        minRows={3}
      />

      <Box>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={submitting || !feedback.overallRating}
        >
          {submitting ? 'Submitting…' : 'Submit Feedback'}
        </Button>
        {!feedback.overallRating && (
          <Typography variant="caption" color="text.secondary" sx={{ ml: 1.5 }}>
            Please give an overall rating first.
          </Typography>
        )}
      </Box>
    </Stack>
  )
}

function YesNoSomewhatQuestion({
  label,
  value,
  onChange,
}: {
  label: string
  value: YesNoSomewhat
  onChange: (value: YesNoSomewhat) => void
}) {
  return (
    <FormControl>
      <FormLabel>{label}</FormLabel>
      <RadioGroup
        row
        value={value}
        onChange={(e) => onChange(e.target.value as YesNoSomewhat)}
      >
        <FormControlLabel value="yes" control={<Radio />} label="Yes" />
        <FormControlLabel value="somewhat" control={<Radio />} label="Somewhat" />
        <FormControlLabel value="no" control={<Radio />} label="No" />
      </RadioGroup>
    </FormControl>
  )
}

function YesNoQuestion({
  label,
  value,
  onChange,
}: {
  label: string
  value: YesNo
  onChange: (value: YesNo) => void
}) {
  return (
    <FormControl>
      <FormLabel>{label}</FormLabel>
      <RadioGroup row value={value} onChange={(e) => onChange(e.target.value as YesNo)}>
        <FormControlLabel value="no" control={<Radio />} label="No" />
        <FormControlLabel value="yes" control={<Radio />} label="Yes" />
      </RadioGroup>
    </FormControl>
  )
}
