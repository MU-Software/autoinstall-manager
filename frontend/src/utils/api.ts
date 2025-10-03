import * as R from 'remeda'

import type { ErrorResponseSchema } from '@frontend/schemas/api'

export const isObjectErrorResponseSchema = (obj?: unknown): obj is ErrorResponseSchema => {
  return (
    R.isPlainObject(obj) &&
    R.isString(obj.type) &&
    R.isArray(obj.errors) &&
    obj.errors.every((error) => {
      return R.isPlainObject(error) && R.isString(error.code) && R.isString(error.detail) && (error.attr === null || R.isString(error.attr))
    })
  )
}
