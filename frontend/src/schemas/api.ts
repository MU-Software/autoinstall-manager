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

export type EnumValue = {
  const: string // UUID
  title: string
}

export type ListValue = {
  id: string
  title: string
  created_at: string
  updated_at: string
}
