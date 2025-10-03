import { Stack } from '@mui/material'
import * as React from 'react'

export const CenteredPage: React.FC<React.PropsWithChildren> = ({ children }) => (
  <Stack justifyContent="center" alignItems="center" sx={{ minHeight: '80vh', maxHeight: '100%' }} children={children} />
)
