import { Add } from '@mui/icons-material'
import { Box, Button, CircularProgress, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material'
import { ErrorBoundary, Suspense } from '@suspensive/react'
import * as React from 'react'

import { ErrorFallback } from '@frontend/elements/error_handler'
import { LinkHandler } from '@frontend/elements/link_handler'
import { useAPIClient, useListQuery } from '@frontend/hooks/useAPI'

const EVEN = 'rgba(0, 0, 0, 0)'
const ODD = 'rgba(0, 0, 0, 0.1)'
const HOVER = 'rgba(0, 0, 0, 0.2)'

export const ListPage: React.FC<{ resource: string }> = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, ({ resource }) => {
    const apiClient = useAPIClient()
    const listQuery = useListQuery(apiClient, resource)

    return (
      <Stack sx={{ flexGrow: 1, width: '100%', minHeight: '100%' }}>
        <Typography variant="h5" children={`${resource.toUpperCase()} > 목록`} />
        <br />
        <Box>
          <LinkHandler href={`/${resource}/create`}>
            <Button variant="contained" startIcon={<Add />} children="새 객체 추가" />
          </LinkHandler>
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: '25%' }} children="ID" />
              <TableCell sx={{ width: '40%' }} children="이름" />
              <TableCell sx={{ width: '17.5%' }} children="생성 시간" />
              <TableCell sx={{ width: '17.5%' }} children="수정 시간" />
            </TableRow>
          </TableHead>
          <TableBody>
            {listQuery.data
              ?.sort((a, b) => a.title.localeCompare(b.title))
              .map((item, index) => (
                <TableRow key={item.id} sx={{ backgroundColor: index % 2 === 0 ? EVEN : ODD, '&:hover': { backgroundColor: HOVER } }}>
                  <TableCell children={<LinkHandler href={`/${resource}/${item.id}`} children={item.id} />} />
                  <TableCell children={<LinkHandler href={`/${resource}/${item.id}`} children={item.title} />} />
                  <TableCell children={new Date(item.created_at).toLocaleString()} />
                  <TableCell children={new Date(item.updated_at).toLocaleString()} />
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </Stack>
    )
  })
)
