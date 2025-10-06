import { CssBaseline, ThemeProvider } from '@mui/material'
import { ErrorBoundary } from '@suspensive/react'
import { matchQuery, MutationCache, Query, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { SnackbarProvider } from 'notistack'
import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import type { ContextOptions } from '@frontend/contexts'
import { AppContextProvider } from '@frontend/elements/app_context'
import { MainLayout } from '@frontend/layouts/main_layout'
import { ErrorPage } from '@frontend/pages/commons/error_page'

import { routes } from './router'
import { canonicalTheme } from './theme'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      gcTime: 24 * 60 * 60 * 1000, // 24 hours
      staleTime: 3 * 60 * 1000, // 3 minutes
      refetchOnWindowFocus: false,
    },
  },
  mutationCache: new MutationCache({
    onSuccess: (_data, _var, _ctx, mut) => {
      const predicate = (q: Query) => mut.meta?.invalidates?.some((queryKey) => matchQuery({ queryKey }, q)) ?? true
      queryClient.resetQueries({ predicate })
    },
  }),
})

const appContextOptions: ContextOptions = {
  debug: import.meta.env.MODE === 'development',
  apiDomain: import.meta.env.VITE_API_DOMAIN || '',
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <SnackbarProvider>
      <ThemeProvider theme={canonicalTheme}>
        <CssBaseline />
        <AppContextProvider options={appContextOptions}>
          <QueryClientProvider client={queryClient}>
            <ReactQueryDevtools initialIsOpen={false} />
            <ErrorBoundary fallback={ErrorPage}>
              <RouterProvider router={createBrowserRouter([{ path: '/', Component: MainLayout, children: routes }])} />
            </ErrorBoundary>
          </QueryClientProvider>
        </AppContextProvider>
      </ThemeProvider>
    </SnackbarProvider>
  </React.StrictMode>
)
