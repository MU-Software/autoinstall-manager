import { Add, Delete, Edit } from '@mui/icons-material'
import type { ButtonProps, OutlinedSelectProps } from '@mui/material'
import {
  Box,
  Button,
  Chip,
  CircularProgress,
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
import type { Field, FieldProps, RJSFSchema } from '@rjsf/utils'
import { customizeValidator } from '@rjsf/validator-ajv8'
import { ErrorBoundary, Suspense } from '@suspensive/react'
import AjvDraft04 from 'ajv-draft-04'
import type { JSONSchema7 } from 'json-schema'
import React from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import * as R from 'remeda'

import { retrieve } from '@frontend/apis/api'
import { ErrorFallback } from '@frontend/elements/error_handler'
import { useAPIClient, useCreateMutation, useRemoveMutation, useSchemaQuery, useUpdateMutation } from '@frontend/hooks/useAPI'
import { filterReadOnlyPropertiesInJsonSchema, filterWritablePropertiesInJsonSchema } from '@frontend/utils/json_schema'
import { addErrorSnackbar, addSnackbar } from '@frontend/utils/snackbar'
import { isNumeric } from '@frontend/utils/string'

type EditorFormDataEventType = IChangeEvent<Record<string, string>, RJSFSchema, { [k in string]: unknown }>
type onSubmitType = (data: Record<string, string>, event: React.FormEvent<unknown>) => void

type AppResourceIdType = { resource: string; id?: string }
type EditorPropsType = React.PropsWithChildren<{
  resource: string
  initialData?: Record<string, string>
  beforeSubmit?: onSubmitType
  afterSubmit?: onSubmitType
  extraActions?: ButtonProps[]
}>

type DescriptiveEnum = { const: string; title: string }
type DescriptiveEnumObject = Record<string, DescriptiveEnum>

const SelectedChipRenderer: React.FC<{ selectable: DescriptiveEnumObject; selected: string[] }> = ({ selectable, selected }) => {
  const children = selected.map((v) => <Chip key={v} label={selectable[v].title || ''} />)
  return <Stack sx={{ flexWrap: 'wrap' }} direction="row" spacing={0.5} children={children} />
}

const fieldPropsToSelectedProps = (props: FieldProps): OutlinedSelectProps & { defaultValue: string[] } => {
  const {
    name,
    formData,
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
  const data = {
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
  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => rawOnChange(event.target.value, undefined, event.target.name)
  const sx: OutlinedSelectProps['sx'] = color ? { color, borderColor: color } : {}
  const defaultValue = (formData ? (R.isArray(formData) ? formData : [formData.toString()]) : []) as string[]
  return R.addProp({ ...rest, name, label: name, defaultValue, autoFocus, readOnly, onFocus, onBlur, onChange, sx }, 'data-rjsf', data)
}

const M2MSelect: Field = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, (props) => {
    const selectable = (props.schema.items as JSONSchema7).oneOf as DescriptiveEnum[]
    const selectableListObj: DescriptiveEnumObject = selectable.reduce((a, i) => ({ ...a, [i.const]: i }), {} as DescriptiveEnumObject)
    const children = selectable.map((i) => <MenuItem key={i.const} value={i.const} children={i.title || i.const} />)
    const selectRenderer = (selected: string[]) => <SelectedChipRenderer selectable={selectableListObj} selected={selected} />
    return (
      <FormControl fullWidth>
        <InputLabel id={`${props.name}-label`} children={props.name} />
        <Select {...fieldPropsToSelectedProps(props)} children={children} multiple fullWidth renderValue={selectRenderer} />
      </FormControl>
    )
  })
)

export const Editor: React.FC<AppResourceIdType & EditorPropsType> = ErrorBoundary.with(
  { fallback: ErrorFallback },
  Suspense.with({ fallback: <CircularProgress /> }, ({ resource, id, initialData, beforeSubmit, afterSubmit, extraActions, children }) => {
    const navigate = useNavigate()
    const formRef = React.useRef<Form<Record<string, string>, RJSFSchema, { [k in string]: unknown }> | null>(null)

    const [editorState, setEditorState] = React.useState<Record<string, string>>(initialData || {})
    const appendFormDataState = (data: Record<string, string>) => setEditorState((ps) => ({ ...ps, ...data }))

    const apiClient = useAPIClient()
    const { data: schemaInfo } = useSchemaQuery(apiClient, resource)
    const createMutation = useCreateMutation<Record<string, string>>(apiClient, resource)
    const modifyMutation = useUpdateMutation<Record<string, string>>(apiClient, resource, id || 'undefined')
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
            <MuiForm
              ref={formRef}
              schema={writableSchema}
              uiSchema={{
                ...schemaInfo.ui_schema,
                'ui:submitButtonOptions': { norender: true },
              }}
              validator={customizeValidator({ AjvClass: AjvDraft04 })}
              formData={editorState.formData}
              liveValidate
              focusOnFirstError
              formContext={{ readonlyAsDisabled: true }}
              onChange={({ formData }) => appendFormDataState(formData)}
              onSubmit={onSubmitFunc}
              disabled={disabled}
              showErrorList={false}
              fields={{ m2m_select: M2MSelect }}
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

  return <Suspense fallback={<CircularProgress />} children={<PreparedEditor {...props} id={id} />} />
}
