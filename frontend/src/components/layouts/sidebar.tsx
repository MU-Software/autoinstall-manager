import type { AppBarProps, CSSObject, Theme } from '@mui/material'
import { AppBar, Drawer, styled } from '@mui/material'

const drawerExpandWidth = 240

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerExpandWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
})

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: { width: `calc(${theme.spacing(8)} + 1px)` },
})

export const MiniVariantAppBar = styled(AppBar, { shouldForwardProp: (prop) => prop !== 'open' })<AppBarProps & { open?: boolean }>(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  variants: [
    {
      props: ({ open }) => open,
      style: {
        marginLeft: drawerExpandWidth,
        width: `calc(100% - ${drawerExpandWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
    },
  ],
}))

export const MiniVariantDrawer = styled(Drawer, { shouldForwardProp: (prop) => prop !== 'open' })(({ theme }) => ({
  flexShrink: 0,
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
  variants: [
    { props: ({ open }) => open, style: { ...openedMixin(theme), '& .MuiDrawer-paper': openedMixin(theme) } },
    { props: ({ open }) => !open, style: { ...closedMixin(theme), '& .MuiDrawer-paper': closedMixin(theme) } },
  ],
}))
