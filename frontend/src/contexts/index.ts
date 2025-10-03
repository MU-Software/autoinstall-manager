import React from 'react'

export type ContextOptions = {
  debug?: boolean
  apiDomain: string
  apiTimeout: number
}

export const appContext = React.createContext<ContextOptions>({
  debug: false,
  apiDomain: '',
  apiTimeout: 10000,
})
