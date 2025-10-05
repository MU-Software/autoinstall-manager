import { Add, Delete, Edit } from '@mui/icons-material'
import type { ButtonProps, SelectChangeEvent, SelectProps } from '@mui/material'
import {
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import Form, { type IChangeEvent } from '@rjsf/core'
import MuiForm from '@rjsf/mui'
import type { Field, FieldProps, RJSFSchema, UiSchema } from '@rjsf/utils'
import { customizeValidator } from '@rjsf/validator-ajv8'
import { ErrorBoundary, Suspense } from '@suspensive/react'
import AjvDraft04 from 'ajv-draft-04'
import type { JSONSchema7 } from 'json-schema'
import React from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'

import { ErrorFallback } from '@frontend/elements/error_handler'
import {
  useAPIClient,
  useCreateMutation,
  useListSelectableEnumsQuery,
  useRemoveMutation,
  useRetrieveQuery,
  useSchemaQuery,
  useUpdateMutation,
} from '@frontend/hooks/useAPI'
import { filterReadOnlyPropertiesInJsonSchema, filterWritablePropertiesInJsonSchema } from '@frontend/utils/json_schema'
import { addErrorSnackbar, addSnackbar } from '@frontend/utils/snackbar'
import { isUUID } from '@frontend/utils/string'

type EditorFormDataEventType = IChangeEvent<Record<string, string>, RJSFSchema, { [k in string]: unknown }>
type onSubmitType = (data: Record<string, string>, event: React.FormEvent<unknown>) => void

type EditorPropsType = React.PropsWithChildren<{
  resource: string
  initialData?: Record<string, string>
  beforeSubmit?: onSubmitType
  afterSubmit?: onSubmitType
  extraActions?: ButtonProps[]
}>

type CustomMUISelectedAdditionalData = {
  schema: JSONSchema7
  errorSchema?: RJSFSchema
  uiSchema?: Record<string, UiSchema>
  idSchema: { $id: string; [k: string]: unknown }
  formContext: { [k: string]: unknown }
  wasPropertyKeyModified?: boolean
  registry: unknown
  rawErrors?: string[]
  hideError?: boolean
  idPrefix?: string
  idSeparator?: string
}

const isNullableField = (schema: JSONSchema7): boolean => {
  if (Array.isArray(schema.type)) return schema.type.includes('null')

  const anyOfOrOneOf = schema.anyOf || schema.oneOf
  if (anyOfOrOneOf) {
    for (const subSchema of anyOfOrOneOf) if (isNullableField(subSchema as JSONSchema7)) return true
    return false
  }

  return schema.type === 'null'
}

const rjsfFieldPropsToMUISelectedProps = (props: FieldProps): SelectProps & { additionaldata: CustomMUISelectedAdditionalData } => {
  const {
    name,
    formData: defaultValue,
    autofocus: autoFocus,
    readonly: readOnly,
    onFocus: rawOnFocus,
    onBlur: rawOnBlur,
    onChange: rawOnChange,

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    required: _,

    schema,
    errorSchema,
    uiSchema,
    idSchema,
    formContext,
    wasPropertyKeyModified,
    registry,
    rawErrors,
    hideError,
    idPrefix,
    idSeparator,
    color,
    ...rest
  } = props
  const additionaldata: CustomMUISelectedAdditionalData = {
    schema,
    errorSchema,
    uiSchema,
    idSchema,
    formContext,
    wasPropertyKeyModified,
    registry,
    rawErrors,
    hideError,
    idPrefix,
    idSeparator,
  }
  const onFocus = (event: React.FocusEvent<HTMLInputElement>) => rawOnFocus(event.currentTarget.name, event.currentTarget.value)
  const onBlur = (event: React.FocusEvent<HTMLInputElement>) => rawOnBlur(event.currentTarget.name, event.currentTarget.value)
  const onChange = (event: SelectChangeEvent<unknown>) => rawOnChange(event.target.value, undefined, event.target.name)
  const sx: SelectProps['sx'] = color ? { color, borderColor: color } : {}
  return { ...rest, name, label: name, defaultValue, autoFocus, readOnly, onFocus, onBlur, onChange, sx, additionaldata }
}

const ForeignKeyField: Field = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, (props) => {
    const selectedProps = rjsfFieldPropsToMUISelectedProps(props)

    const uiOptions = selectedProps.additionaldata.uiSchema?.['ui:options']
    if (!uiOptions) throw new Error('ui:options is undefined in uiSchema')

    const resourceName = uiOptions.resourceName
    if (!resourceName) throw new Error('resourceName is undefined in ui:options of uiSchema')

    const apiClient = useAPIClient()
    const { data } = useListSelectableEnumsQuery(apiClient, resourceName)

    const children = data.map((i) => <MenuItem key={i.const} value={i.const} children={i.title} />)
    if (isNullableField(selectedProps.additionaldata.schema)) children.unshift(<MenuItem key="__null__" children="(없음)" />)

    return (
      <FormControl fullWidth>
        <InputLabel id={`${props.name}-label`} children={props.name} />
        <Select {...selectedProps} labelId={`${props.name}-label`} children={children} fullWidth />
      </FormControl>
    )
  })
)

export const Editor: React.FC<EditorPropsType & { id?: string }> = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, ({ resource, id, initialData, beforeSubmit, afterSubmit, extraActions, children }) => {
    const navigate = useNavigate()
    const formRef = React.useRef<Form<Record<string, string>, RJSFSchema, { [k in string]: unknown }> | null>(null)

    const [editorState, setEditorState] = React.useState<Record<string, string>>(initialData || {})
    const appendFormDataState = (data: Record<string, string>) => setEditorState((ps) => ({ ...ps, ...data }))

    const apiClient = useAPIClient()
    const { data: schemaInfo } = useSchemaQuery(apiClient, resource)
    const createMutation = useCreateMutation<Record<string, string>>(apiClient, resource)
    const modifyMutation = useUpdateMutation<Record<string, string>>(apiClient, resource)
    const deleteMutation = useRemoveMutation(apiClient, resource, id || 'undefined')
    const submitMutation = id ? modifyMutation : createMutation

    const onSubmitButtonClick: React.MouseEventHandler<HTMLButtonElement> = () => formRef.current && formRef.current.submit()

    const onSubmitFunc = (data: EditorFormDataEventType, event: React.FormEvent) => {
      const newFormData = editorState || data.formData
      beforeSubmit?.(newFormData, event)
      submitMutation.mutate(newFormData, {
        onSuccess: (newFormData) => {
          addSnackbar(id ? '저장했습니다.' : '생성했습니다.', 'success')
          afterSubmit?.(newFormData, event)

          if (!id && newFormData.id) navigate(`/${resource}/${newFormData.id}`)
        },
        onError: addErrorSnackbar,
      })
    }

    const onDeleteFunc = () => {
      if (window.confirm('정말로 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        deleteMutation.mutate(undefined, {
          onSuccess: () => {
            addSnackbar('삭제했습니다.', 'success')
            navigate(`/${resource}`)
          },
          onError: addErrorSnackbar,
        })
      }
    }

    const goToCreateNew = () => navigate(`/${resource}/create`)

    const writableSchema = filterWritablePropertiesInJsonSchema(schemaInfo.schema)
    const readOnlySchema = filterReadOnlyPropertiesInJsonSchema(schemaInfo.schema)
    const disabled = createMutation.isPending || modifyMutation.isPending || deleteMutation.isPending

    const handleCtrlSAction: (this: GlobalEventHandlers, ev: KeyboardEvent) => void = (event) => {
      if (event.key === 's' && (event.ctrlKey || event.metaKey)) {
        console.log('Ctrl+S pressed, executing save action')
        event.preventDefault()
        event.stopPropagation()
        formRef.current?.submit()
      }
    }

    React.useEffect(() => {
      document.addEventListener('keydown', handleCtrlSAction)
      return () => {
        console.log('Removing event listener for Ctrl+S action')
        document.removeEventListener('keydown', handleCtrlSAction)
      }
    }, [])

    return (
      <Box sx={{ flexGrow: 1, width: '100%', minHeight: '100%' }}>
        <Stack direction="row" justifyContent="space-between">
          <Typography variant="h5" children={`${resource.toUpperCase()} > ${id ? `편집: ${id}` : '새 객체 추가'}`} />
        </Stack>
        <Stack direction="row" spacing={2} sx={{ width: '100%', height: '100%', maxWidth: '100%' }}>
          <Box sx={{ flexGrow: 1 }}>
            {id && (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell children="필드" />
                    <TableCell children="값" />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.keys(readOnlySchema.properties || {}).map((key) => (
                    <TableRow key={key}>
                      <TableCell children={key} />
                      <TableCell children={editorState[key]} />
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            <Divider sx={{ my: 2 }} />
            <MuiForm
              ref={formRef}
              schema={writableSchema}
              uiSchema={{
                ...schemaInfo.ui_schema,
                'ui:options': { label: false, submitOnEnter: false },
                'ui:submitButtonOptions': { norender: true },
              }}
              validator={customizeValidator({ AjvClass: AjvDraft04 })}
              formData={editorState}
              liveValidate
              focusOnFirstError
              formContext={{ readonlyAsDisabled: true }}
              onChange={({ formData }) => appendFormDataState(formData)}
              onSubmit={onSubmitFunc}
              disabled={disabled}
              showErrorList={false}
              fields={{ ForeignKeyField }}
            />
          </Box>
        </Stack>
        {children}
        <Stack direction="row" spacing={2} sx={{ justifyContent: 'flex-end' }}>
          {id ? (
            <>
              {(extraActions || []).map((p, i) => (
                <Button key={i} {...p} />
              ))}
              <Button variant="outlined" color="info" onClick={goToCreateNew} disabled={disabled} startIcon={<Add />} children="새 객체 추가" />
              <Button variant="outlined" color="error" onClick={onDeleteFunc} disabled={disabled} startIcon={<Delete />} children="삭제" />
              <Button variant="contained" color="primary" onClick={onSubmitButtonClick} disabled={disabled} startIcon={<Edit />} children="수정" />
            </>
          ) : (
            <Button
              type="submit"
              variant="contained"
              color="primary"
              onClick={onSubmitButtonClick}
              disabled={disabled}
              startIcon={<Add />}
              children="새 객체 추가"
            />
          )}
        </Stack>
      </Box>
    )
  })
)

const PreparedEditor: React.FC<EditorPropsType & { id: string }> = ({ id, ...props }) => {
  const apiClient = useAPIClient()
  const { data } = useRetrieveQuery<Record<string, string>>(apiClient, props.resource, id)
  return <Editor {...props} initialData={{ ...data, ...props.initialData }} id={id} />
}

export const EditorRoutePage: React.FC<EditorPropsType> = (props) => {
  const { id } = useParams<{ id?: string }>()
  if (id === 'create') return <Editor {...props} />

  const { resource } = props
  if (!isUUID(id)) {
    alert('유효하지 않은 ID입니다.')
    return <Navigate to={`/${resource}`} replace />
  }

  return (
    <ErrorBoundary fallback={ErrorFallback}>
      <Suspense fallback={<CircularProgress />}>
        <PreparedEditor {...props} id={id} />
      </Suspense>
    </ErrorBoundary>
  )
}
