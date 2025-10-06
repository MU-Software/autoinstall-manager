import { LinkHandler } from '@frontend/elements/link_handler'
import { MiniVariantAppBar, MiniVariantDrawer } from '@frontend/layouts/sidebar'
import { ChevronLeft, Menu } from '@mui/icons-material'
import {
  Box,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  styled,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material'
import React from 'react'
import { Outlet, useNavigate } from 'react-router-dom'

import { routes } from '../../router'

const ExpandButtonContainer = styled(Stack)(({ theme }) => ({
  justifyContent: 'center',
  alignItems: 'center',

  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: { width: `calc(${theme.spacing(8)} + 1px)` },
}))

export const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const [openDrawer, dispatch] = React.useState<boolean>(false)
  const toggleDrawer = () => dispatch((ps) => !ps)

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <MiniVariantAppBar position="fixed" open={openDrawer}>
        <Toolbar disableGutters>
          <ExpandButtonContainer>
            <Tooltip title="Menu">
              <IconButton color="inherit" onClick={toggleDrawer}>
                {openDrawer ? <ChevronLeft /> : <Menu />}
              </IconButton>
            </Tooltip>
          </ExpandButtonContainer>
          <LinkHandler href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Typography variant="h6" sx={{ px: 2, fontWeight: 700 }} children="autoinstall manager" />
          </LinkHandler>
        </Toolbar>
      </MiniVariantAppBar>
      <Toolbar />
      <Stack direction="row" sx={{ width: '100%', height: '100%' }}>
        <MiniVariantDrawer variant="permanent" open={openDrawer}>
          <Toolbar disableGutters />
          <Divider />
          <Stack sx={{ height: '100%', overflowX: 'hidden', gap: 1, py: 1 }}>
            {routes
              .filter((r) => r.showInSidebar)
              .map((r) => (
                <ListItem key={r.path} disablePadding>
                  <ListItemButton sx={{ minHeight: 48, px: 2.5, gap: 3 }} onClick={() => navigate(r.path || '')}>
                    <ListItemIcon sx={{ minWidth: 0, justifyContent: 'center' }} children={<r.icon />} />
                    <ListItemText primary={r.title} />
                  </ListItemButton>
                </ListItem>
              ))}
          </Stack>
        </MiniVariantDrawer>
        <Outlet />
      </Stack>
    </Box>
  )
}
