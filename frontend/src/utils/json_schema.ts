import type { JSONSchema7 } from 'json-schema'

export const filterWritablePropertiesInJsonSchema = (schema: JSONSchema7) => {
  const writableSchema: JSONSchema7 = { ...schema }
  if (writableSchema.properties) {
    writableSchema.properties = Object.entries(writableSchema.properties)
      .filter(([, propDef]) => !(propDef as JSONSchema7).readOnly)
      .reduce(
        (acc, [propKey, propDef]) => ({
          ...acc,
          [propKey]: filterWritablePropertiesInJsonSchema(propDef as JSONSchema7),
        }),
        {} as JSONSchema7['properties']
      )
  }

  return writableSchema
}

export const filterReadOnlyPropertiesInJsonSchema = (schema: JSONSchema7) => {
  const readOnlySchema: JSONSchema7 = { ...schema }
  if (readOnlySchema.properties) {
    readOnlySchema.properties = Object.entries(readOnlySchema.properties)
      .filter(([, propDef]) => (propDef as JSONSchema7).readOnly)
      .reduce(
        (acc, [propKey, propDef]) => ({
          ...acc,
          [propKey]: filterReadOnlyPropertiesInJsonSchema(propDef as JSONSchema7),
        }),
        {} as JSONSchema7['properties']
      )
    readOnlySchema.required = readOnlySchema.required?.filter((key) => key in (readOnlySchema?.properties || {}))
  }

  return readOnlySchema
}

type SupportedLanguage = 'ko' | 'en'

export const filterPropertiesByLanguageInJsonSchema = (schema: JSONSchema7, translation_fields: string[] = [], language: SupportedLanguage) => {
  const filteredSchema: JSONSchema7 = { ...schema }
  if (translation_fields.length === 0) return filteredSchema

  const notSelectedLanguage = language === 'ko' ? 'en' : 'ko'
  const notSelectedLangFields = translation_fields.map((f) => `${f}_${notSelectedLanguage}`)
  if (filteredSchema.properties) {
    filteredSchema.properties = Object.entries(filteredSchema.properties)
      .filter(([key]) => !notSelectedLangFields.includes(key))
      .reduce(
        (acc, [propKey, propDef]) => ({
          ...acc,
          [propKey]: filterPropertiesByLanguageInJsonSchema(propDef as JSONSchema7, translation_fields, language),
        }),
        {} as JSONSchema7['properties']
      )
  }

  return filteredSchema
}
