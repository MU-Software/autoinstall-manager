import { AppBar, Box, Toolbar, Typography } from '@mui/material'
import React from 'react'

export const App: React.FC = () => {
  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <AppBar>
        <Toolbar disableGutters>
          <Typography />
        </Toolbar>
      </AppBar>
      <Toolbar />
      <Box>Home</Box>
    </Box>
  )
}
