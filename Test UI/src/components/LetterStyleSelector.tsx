import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  Stack,
  Typography,
} from '@mui/material'
import { letterStyles } from '../types'
import type { LetterStyleId } from '../types'

interface LetterStyleSelectorProps {
  value: LetterStyleId
  onChange: (style: LetterStyleId) => void
  disabled?: boolean
}

/**
 * Picks which letter style to generate. Both styles are clinically identical —
 * same notes, same sections, same rules — so this only changes presentation.
 */
export function LetterStyleSelector({ value, onChange, disabled }: LetterStyleSelectorProps) {
  return (
    <FormControl disabled={disabled} sx={{ width: '100%' }}>
      <FormLabel sx={{ mb: 1, fontWeight: 600 }}>Letter style</FormLabel>
      <RadioGroup
        value={value}
        onChange={(e) => onChange(e.target.value as LetterStyleId)}
        sx={{ gap: 1 }}
      >
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          {letterStyles.map((style) => {
            const selected = style.id === value
            return (
              <Paper
                key={style.id}
                variant="outlined"
                onClick={() => !disabled && onChange(style.id)}
                sx={{
                  flex: 1,
                  px: 1.5,
                  py: 1,
                  cursor: disabled ? 'default' : 'pointer',
                  borderColor: selected ? 'primary.main' : 'divider',
                  borderWidth: selected ? 2 : 1,
                  bgcolor: selected ? 'action.hover' : 'background.paper',
                  transition: 'border-color 120ms, background-color 120ms',
                }}
              >
                <FormControlLabel
                  value={style.id}
                  control={<Radio size="small" />}
                  disabled={disabled}
                  sx={{ m: 0, alignItems: 'flex-start' }}
                  label={
                    <span>
                      <Typography variant="body2" fontWeight={600}>
                        {style.label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {style.description}
                      </Typography>
                    </span>
                  }
                />
              </Paper>
            )
          })}
        </Stack>
      </RadioGroup>
    </FormControl>
  )
}
