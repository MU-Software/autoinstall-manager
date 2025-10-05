import type { EnumValue, ListValue, SchemaDefinition } from '@frontend/schemas/api'
import { APIClient } from './client'

export const list = (client: APIClient, resource: string, params?: Record<string, string>) => () =>
  client.get<ListValue[]>(`${resource}/`, { params })

export const retrieve =
  <T>(client: APIClient, resource: string, id: string) =>
  () => {
    if (!id) return Promise.resolve(null)
    return client.get<T>(`${resource}/${id}/`)
  }

export const create =
  <T>(client: APIClient, resource: string) =>
  (data: Omit<T, 'id'>) =>
    client.post<T, Omit<T, 'id'>>(`${resource}/`, data)

export const update =
  <T>(client: APIClient, resource: string) =>
  (data: T) =>
    client.put<T, T>(`${resource}`, data)

export const updatePrepared =
  <T>(client: APIClient, resource: string) =>
  (data: T) =>
    client.put<T, T>(`${resource}`, data)

export const remove = (client: APIClient, resource: string, id: string) => () => client.delete<void>(`${resource}/${id}/`)

export const removePrepared = (client: APIClient, resource: string) => (id: string) => client.delete<void>(`${resource}/${id}/`)

export const schema = (client: APIClient, resource: string) => () => client.get<SchemaDefinition>(`json-schemas/${resource}`)

export const listSelectableEnums = (client: APIClient, resource: string) => () => client.get<EnumValue[]>(`${resource}/enum-values/`)
