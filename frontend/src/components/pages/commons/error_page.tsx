import type { ErrorBoundaryFallbackProps } from '@suspensive/react'
import type React from 'react'

import { ErrorFallback } from '@frontend/elements/error_handler'
import { CenteredPage } from '@frontend/layouts/centered_page'

export const ErrorPage: React.FC<ErrorBoundaryFallbackProps> = (props) => <CenteredPage children={<ErrorFallback {...props} />} />
