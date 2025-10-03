import { Button, Typography, styled } from '@mui/material'
import type { ErrorBoundaryFallbackProps } from '@suspensive/react'
import type React from 'react'

const PreWrappedPre = styled('pre')({
  whiteSpace: 'pre-wrap',
  backgroundColor: '#f5f5f5',
  padding: '1em',
  borderRadius: '4px',
  userSelect: 'text',
})

export const ErrorFallback: React.FC<ErrorBoundaryFallbackProps> = ({ error, reset }) => {
  console.error(error)
  const errorObject = Object.getOwnPropertyNames(error).reduce(
    (acc, key) => ({ ...acc, [key]: (error as unknown as Record<string, unknown>)[key] }),
    {}
  )

  return (
    <>
      <Typography variant="body2" color="error" children={`error.message = ${error.message}`} />
      <details open>
        <summary children="오류 상세" />
        <PreWrappedPre children={<code children={JSON.stringify(errorObject, null, 2)} />} />
      </details>
      <br />
      <Button variant="outlined" onClick={reset} children="다시 시도" />
    </>
  )
}
