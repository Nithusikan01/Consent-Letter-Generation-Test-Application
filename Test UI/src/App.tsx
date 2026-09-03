import { useRef, useState } from 'react'
import type { ReactNode } from 'react'
import {
  Alert,
  AppBar,
  Box,
  Container,
  Divider,
  Paper,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material'
import { LetterForm } from './components/LetterForm'
import { TestCaseSelector } from './components/TestCaseSelector'
import { GeneratedLetterView } from './components/GeneratedLetterView'
import { FeedbackForm } from './components/FeedbackForm'
import { generatePatientLetter, submitFeedback } from './api/letterApi'
import { testCases } from './data/testCases'
import { emptyFormValues } from './types'
import type { FeedbackData, GenerateLetterResponse, LetterFormValues } from './types'

function SectionCard({
  step,
  title,
  children,
}: {
  step: number
  title: string
  children: ReactNode
}) {
  return (
    <Paper elevation={1} sx={{ p: { xs: 2.5, sm: 4 } }}>
      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2.5 }}>
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.9rem',
            fontWeight: 700,
            flexShrink: 0,
          }}
        >
          {step}
        </Box>
        <Typography variant="h2">{title}</Typography>
      </Stack>
      {children}
    </Paper>
  )
}

function App() {
  const [selectedTestCaseId, setSelectedTestCaseId] = useState('')
  const [formValues, setFormValues] = useState<LetterFormValues>(emptyFormValues)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [generatedLetter, setGeneratedLetter] = useState<GenerateLetterResponse | null>(null)

  const letterSectionRef = useRef<HTMLDivElement>(null)
  const formSectionRef = useRef<HTMLDivElement>(null)

  const handleSelectTestCase = (id: string) => {
    setSelectedTestCaseId(id)
    const testCase = testCases.find((tc) => tc.id === id)
    if (testCase) {
      setFormValues(testCase.values)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    setGeneratedLetter(null)
    try {
      const result = await generatePatientLetter(formValues)
      setGeneratedLetter(result)
      requestAnimationFrame(() => {
        letterSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong generating the letter.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAgain = () => {
    setGeneratedLetter(null)
    setError(null)
    requestAnimationFrame(() => {
      formSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }

  const handleFeedbackSubmit = async (feedback: FeedbackData) => {
    if (!generatedLetter) return
    await submitFeedback({
      feedback,
      formValues,
      letterHtml: generatedLetter.html,
      submittedAt: new Date().toISOString(),
    })
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" color="primary" elevation={0}>
        <Toolbar>
          <Stack>
            <Typography variant="h1" sx={{ fontSize: '1.25rem', color: 'inherit' }}>
              Patient Letter Tester
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.85 }}>
              Meditude — Consent Letter Generation Evaluation Tool
            </Typography>
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ py: { xs: 3, sm: 5 } }}>
        <Stack spacing={4}>
          <Alert severity="info" variant="outlined">
            Select a test case or enter your own notes, generate a letter, then read it against
            the original notes and leave feedback. This tool is for evaluation only — do not
            enter real patient information.
          </Alert>

          <div ref={formSectionRef}>
            <SectionCard step={1} title="Choose a test case or enter notes">
              <TestCaseSelector selectedId={selectedTestCaseId} onSelect={handleSelectTestCase} />
            </SectionCard>
          </div>

          <SectionCard step={2} title="Generate the patient letter">
            <LetterForm
              values={formValues}
              onChange={setFormValues}
              onSubmit={handleGenerate}
              loading={loading}
            />
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </SectionCard>

          {generatedLetter && (
            <div ref={letterSectionRef}>
              <SectionCard step={3} title="Generated patient letter">
                <GeneratedLetterView html={generatedLetter.html} onGenerateAgain={handleGenerateAgain} />
              </SectionCard>
            </div>
          )}

          {generatedLetter && (
            <>
              <Divider />
              <SectionCard step={4} title="Give feedback on this letter">
                <FeedbackForm key={generatedLetter.html} onSubmit={handleFeedbackSubmit} />
              </SectionCard>
            </>
          )}
        </Stack>
      </Container>
    </Box>
  )
}

export default App
