import { ErrorBoundary } from '@suspensive/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { SnackbarProvider } from 'notistack'
import React from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'

import type { ContextOptions } from '@frontend/contexts'
import { AppContextProvider } from '@frontend/elements/app_context'
import { ErrorPage } from '@frontend/pages/commons/error_page'
import { router } from './router'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      gcTime: 24 * 60 * 60 * 1000, // 24 hours
      staleTime: 3 * 60 * 1000, // 3 minutes
      refetchOnWindowFocus: false,
    },
  },
})

const appContextOptions: ContextOptions = {
  debug: import.meta.env.MODE === 'development',
  apiDomain: import.meta.env.VITE_API_DOMAIN || '',
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <SnackbarProvider>
      <AppContextProvider options={appContextOptions}>
        <QueryClientProvider client={queryClient}>
          <ReactQueryDevtools initialIsOpen={false} />
          <ErrorBoundary fallback={ErrorPage}>
            <RouterProvider router={router} />
          </ErrorBoundary>
        </QueryClientProvider>
      </AppContextProvider>
    </SnackbarProvider>
  </React.StrictMode>
)
