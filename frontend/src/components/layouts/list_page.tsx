import { Add } from '@mui/icons-material'
import { Button, CircularProgress, Divider, Stack, styled, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material'
import { ErrorBoundary, Suspense } from '@suspensive/react'
import * as React from 'react'
import { useNavigate } from 'react-router-dom'

import { ErrorFallback } from '@frontend/elements/error_handler'
import { LinkHandler } from '@frontend/elements/link_handler'
import { useAPIClient, useListQuery } from '@frontend/hooks/useAPI'

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(even)': { backgroundColor: 'rgba(0, 0, 0, 0)' },
  '&:nth-of-type(odd)': { backgroundColor: 'rgba(0, 0, 0, 0.1)' },
  '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.2)' },
  td: { color: theme.palette.primary.dark },
}))

export const ListPage: React.FC<{ resource: string }> = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, ({ resource }) => {
    const navigate = useNavigate()
    const apiClient = useAPIClient()
    const listQuery = useListQuery(apiClient, resource)

    return (
      <Stack sx={{ flexGrow: 1, width: '100%', minHeight: '100%' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" children={`${resource.toUpperCase()} > 목록`} />
          <LinkHandler href={`/${resource}/create`}>
            <Button variant="contained" startIcon={<Add />} children="새 객체 추가" />
          </LinkHandler>
        </Stack>
        <Divider />
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
              .map((item) => (
                <StyledTableRow key={item.id} onClick={() => navigate(`/${resource}/${item.id}`)} sx={{ cursor: 'pointer' }}>
                  <TableCell children={item.id} />
                  <TableCell children={item.title} />
                  <TableCell children={new Date(item.created_at).toLocaleString()} />
                  <TableCell children={new Date(item.updated_at).toLocaleString()} />
                </StyledTableRow>
              ))}
          </TableBody>
        </Table>
      </Stack>
    )
  })
)
