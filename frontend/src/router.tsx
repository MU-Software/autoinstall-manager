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
        path: '/confignode',
        element: <ListPage resource="confignode" />,
      },
      {
        path: '/confignode/:id',
        element: <EditorRoutePage resource="confignode" />,
      },
      {
        path: '/device',
        element: <ListPage resource="device" />,
      },
      {
        path: '/device/:id',
        element: <EditorRoutePage resource="device" />,
      },
    ],
  },
])
