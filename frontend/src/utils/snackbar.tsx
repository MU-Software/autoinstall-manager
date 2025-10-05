import { Stack } from '@mui/material'
import type { OptionsObject, VariantType } from 'notistack'
import { enqueueSnackbar } from 'notistack'

export const getDefaultSnackOption: (v: VariantType) => OptionsObject = (v) => ({
  variant: v,
  anchorOrigin: { vertical: 'bottom', horizontal: 'center' },
})

export const addSnackbar = (c: string | React.ReactNode, v: VariantType) => enqueueSnackbar(c, getDefaultSnackOption(v))

export const addErrorSnackbar = (error: Error) => {
  console.error(error)
  addSnackbar(
    <Stack>
      에러가 발생했습니다, 콘솔을 확인해주세요.
      <br />
      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{error.message}</pre>
    </Stack>,
    'error'
  )
}
