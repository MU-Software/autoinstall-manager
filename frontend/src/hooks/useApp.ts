import React from 'react'

import { appContext } from '@frontend/contexts'

export const useAppContext = () => {
  const context = React.useContext(appContext)
  if (!context) throw new Error('useAppContext must be used within a CommonProvider')
  return context
}
