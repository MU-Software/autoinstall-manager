import { createBrowserRouter } from 'react-router-dom'

import { EditorRoutePage } from '@frontend/layouts/editor_page'
import { ListPage } from '@frontend/layouts/list_page'
import { MainLayout } from '@frontend/layouts/main_layout'

export const router = createBrowserRouter([
  {
    path: '/',
    Component: MainLayout,
    children: [
      {
        path: '/config-nodes',
        element: <ListPage resource="config-nodes" />,
      },
      {
        path: '/config-nodes/:id',
        element: <EditorRoutePage resource="config-nodes" />,
      },
      {
        path: '/devices',
        element: <ListPage resource="devices" />,
      },
      {
        path: '/devices/:id',
        element: <EditorRoutePage resource="devices" />,
      },
    ],
  },
])
