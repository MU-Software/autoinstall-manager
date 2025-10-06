import { AccountTree, Devices } from '@mui/icons-material'
import type { SvgIconTypeMap } from '@mui/material'
import type { OverridableComponent } from '@mui/material/OverridableComponent'
import type { RouteObject } from 'react-router-dom'

import { EditorRoutePage } from '@frontend/layouts/editor_page'
import { ListPage } from '@frontend/layouts/list_page'

export type ExtendedRouteObject = RouteObject &
  (
    | {
        showInSidebar: true
        icon: OverridableComponent<SvgIconTypeMap<object, 'svg'>> & { muiName: string }
        title: string
      }
    | { showInSidebar: false }
  )

export const routes: ExtendedRouteObject[] = [
  {
    path: '/confignode',
    element: <ListPage resource="confignode" />,
    showInSidebar: true,
    title: 'Config Nodes',
    icon: AccountTree,
  },
  {
    path: '/confignode/:id',
    element: <EditorRoutePage resource="confignode" />,
    showInSidebar: false,
  },
  {
    path: '/device',
    element: <ListPage resource="device" />,
    showInSidebar: true,
    title: 'Devices',
    icon: Devices,
  },
  {
    path: '/device/:id',
    element: <EditorRoutePage resource="device" />,
    showInSidebar: false,
  },
]
