import { useRef, useState } from 'react'
import { Alert, Box, Button, Paper, Snackbar, Stack } from '@mui/material'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import ReplayIcon from '@mui/icons-material/Replay'

interface GeneratedLetterViewProps {
  html: string
  onGenerateAgain: () => void
}

export function GeneratedLetterView({ html, onGenerateAgain }: GeneratedLetterViewProps) {
  const [copied, setCopied] = useState(false)
  const [copyError, setCopyError] = useState(false)
  const letterRef = useRef<HTMLDivElement>(null)

  const handleCopy = async () => {
    const plainText = letterRef.current?.innerText ?? ''
    try {
      if (navigator.clipboard && 'write' in navigator.clipboard && typeof ClipboardItem !== 'undefined') {
        const item = new ClipboardItem({
          'text/html': new Blob([html], { type: 'text/html' }),
          'text/plain': new Blob([plainText], { type: 'text/plain' }),
        })
        await navigator.clipboard.write([item])
      } else {
        await navigator.clipboard.writeText(plainText)
      }
      setCopied(true)
    } catch {
      setCopyError(true)
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={1.5} flexWrap="wrap" alignItems="center">
        <Button variant="outlined" startIcon={<ContentCopyIcon />} onClick={handleCopy}>
          Copy Letter
        </Button>
        <Button variant="text" startIcon={<ReplayIcon />} onClick={onGenerateAgain}>
          Generate Again
        </Button>
      </Stack>

      <Paper
        elevation={2}
        sx={{
          p: { xs: 3, sm: 5 },
          bgcolor: '#ffffff',
          maxWidth: 720,
          mx: 'auto',
          width: '100%',
        }}
      >
        <Box
          ref={letterRef}
          sx={{
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: '1rem',
            lineHeight: 1.7,
            color: '#1c1c1c',
            '& h1, & h2, & h3': {
              fontFamily: '"Inter", "Segoe UI", sans-serif',
              color: '#0f6e5c',
              mt: 3,
              mb: 1.5,
              lineHeight: 1.3,
            },
            '& h1': { fontSize: '1.4rem' },
            '& h2': { fontSize: '1.15rem' },
            '& h3': { fontSize: '1.05rem' },
            '& p': { mb: 2 },
            '& ul, & ol': { mb: 2, pl: 3 },
            '& li': { mb: 0.75 },
            '& strong': { color: '#0f0f0f' },
            '&> *:first-of-type': { mt: 0 },
          }}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      </Paper>

      <Snackbar
        open={copied}
        autoHideDuration={2500}
        onClose={() => setCopied(false)}
        message="Letter copied to clipboard"
      />
      <Snackbar open={copyError} autoHideDuration={4000} onClose={() => setCopyError(false)}>
        <Alert severity="error" onClose={() => setCopyError(false)}>
          Could not copy automatically — please select the text and copy manually.
        </Alert>
      </Snackbar>
    </Stack>
  )
}
