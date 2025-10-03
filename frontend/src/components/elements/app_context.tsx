import type { ContextOptions } from '@frontend/contexts'
import { appContext } from '@frontend/contexts'
import React from 'react'

type ContextOptionsProps = React.PropsWithChildren & { options: ContextOptions }

export const AppContextProvider: React.FC<ContextOptionsProps> = (props) => <appContext.Provider value={props.options} children={props.children} />
