import { Box, MenuItem, Stack, TextField, Typography } from '@mui/material'
import { testCases } from '../data/testCases'

interface TestCaseSelectorProps {
  selectedId: string
  onSelect: (id: string) => void
}

export function TestCaseSelector({ selectedId, onSelect }: TestCaseSelectorProps) {
  const selected = testCases.find((testCase) => testCase.id === selectedId)

  return (
    <Stack spacing={1.5}>
      <TextField
        select
        label="Predefined test case"
        value={selectedId}
        onChange={(e) => onSelect(e.target.value)}
        helperText="Choosing a test case fills in the form below. You can still edit any field before generating."
        fullWidth
      >
        <MenuItem value="">
          <em>None — enter my own details</em>
        </MenuItem>
        {testCases.map((testCase) => (
          <MenuItem key={testCase.id} value={testCase.id}>
            {testCase.label}
          </MenuItem>
        ))}
      </TextField>
      {selected && (
        <Box
          sx={{
            px: 2,
            py: 1,
            bgcolor: 'secondary.main',
            color: 'secondary.contrastText',
            borderRadius: 1,
            opacity: 0.9,
          }}
        >
          <Typography variant="body2">{selected.description}</Typography>
        </Box>
      )}
    </Stack>
  )
}
