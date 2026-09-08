import { useRef, useState } from 'react'
import type { ReactNode } from 'react'
import {
  Alert,
  AppBar,
  Box,
  Container,
  Paper,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material'
import { LetterForm } from './components/LetterForm'
import { TestCaseSelector } from './components/TestCaseSelector'
import { GeneratedLetterView } from './components/GeneratedLetterView'
import { generatePatientLetter } from './api/letterApi'
import { testCases } from './data/testCases'
import { defaultLetterStyle, emptyFormValues } from './types'
import type { GenerateLetterResponse, LetterFormValues, LetterStyleId } from './types'

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
  const [letterStyle, setLetterStyle] = useState<LetterStyleId>(defaultLetterStyle)

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
      const result = await generatePatientLetter(formValues, letterStyle)
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

      <Container maxWidth="lg" sx={{ py: { xs: 3, sm: 5 } }}>
        <Stack spacing={4}>
          <Alert severity="info" variant="outlined">
            Select a test case or enter your own notes, then generate a letter and read it
            against the original notes. This tool is for evaluation only — do not enter real
            patient information.
          </Alert>

          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              alignItems: 'flex-start',
              gap: 4,
            }}
          >
            <Stack spacing={4} sx={{ width: '100%', flex: { md: '0 0 45%' } }}>
              <div ref={formSectionRef}>
                <SectionCard step={1} title="Enter patient details">
                  <Stack spacing={3}>
                    <TestCaseSelector selectedId={selectedTestCaseId} onSelect={handleSelectTestCase} />
                    <LetterForm
                      values={formValues}
                      onChange={setFormValues}
                      onSubmit={handleGenerate}
                      loading={loading}
                      style={letterStyle}
                      onStyleChange={setLetterStyle}
                    />
                    {error && <Alert severity="error">{error}</Alert>}
                  </Stack>
                </SectionCard>
              </div>

              {generatedLetter && (
                <Box sx={{ display: { xs: 'block', md: 'none' } }} ref={letterSectionRef}>
                  <SectionCard step={2} title="Generated patient letter">
                    <GeneratedLetterView
                      html={generatedLetter.html}
                      onGenerateAgain={handleGenerateAgain}
                      style={generatedLetter.style}
                    />
                  </SectionCard>
                </Box>
              )}
            </Stack>

            <Box sx={{ width: '100%', flex: { md: '1 1 55%' }, display: { xs: 'none', md: 'block' } }}>
              {generatedLetter ? (
                <SectionCard step={2} title="Generated patient letter">
                  <GeneratedLetterView
                    html={generatedLetter.html}
                    onGenerateAgain={handleGenerateAgain}
                    style={generatedLetter.style}
                  />
                </SectionCard>
              ) : (
                <Paper
                  variant="outlined"
                  sx={{
                    minHeight: 320,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    p: 4,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    Your generated letter will appear here.
                  </Typography>
                </Paper>
              )}
            </Box>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}

export default App
