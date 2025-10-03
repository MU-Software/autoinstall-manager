import type { RJSFSchema, UiSchema } from '@rjsf/utils'

export type DetailedErrorSchema = {
  code: string
  detail: string
  attr: string | null
}

export type ErrorResponseSchema = {
  type: string
  errors: DetailedErrorSchema[]
}

export type SchemaDefinition = {
  schema: RJSFSchema
  ui_schema: UiSchema
}
