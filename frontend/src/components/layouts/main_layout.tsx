import { AppBar, Box, Toolbar, Typography } from '@mui/material'
import React from 'react'
import { Outlet } from 'react-router-dom'

export const MainLayout: React.FC = () => {
  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <AppBar>
        <Toolbar disableGutters>
          <Typography />
        </Toolbar>
      </AppBar>
      <Toolbar />
      <Box children={<Outlet />} />
    </Box>
  )
}
