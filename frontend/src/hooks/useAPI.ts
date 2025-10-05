import { useMutation, useSuspenseQuery } from '@tanstack/react-query'

import { create, list, listSelectableEnums, remove, removePrepared, retrieve, schema, update, updatePrepared } from '@frontend/apis/api'
import { APIClient } from '@frontend/apis/client'
import { useAppContext } from './useApp'

const QUERY_KEYS = {
  SCHEMA: ['query', 'schema'],
  LIST: ['query', 'list'],
  RETRIEVE: ['query', 'retrieve'],
  LIST_SELECTABLE_ENUMS: ['query', 'list_selectable_enums'],
}

const MUTATION_KEYS = {
  CREATE: ['mutation', 'create'],
  UPDATE: ['mutation', 'update'],
  REMOVE: ['mutation', 'remove'],
}

export const useAPIClient = () => {
  const { apiDomain, apiTimeout } = useAppContext()
  return new APIClient(apiDomain, apiTimeout)
}

export const useSchemaQuery = (client: APIClient, resource: string) =>
  useSuspenseQuery({
    queryKey: [...QUERY_KEYS.SCHEMA, resource],
    queryFn: schema(client, resource),
  })

export const useListSelectableEnumsQuery = (client: APIClient, resource: string) =>
  useSuspenseQuery({
    queryKey: [...QUERY_KEYS.LIST_SELECTABLE_ENUMS, resource],
    queryFn: listSelectableEnums(client, resource),
  })

export const useListQuery = <T>(client: APIClient, resource: string, params?: Record<string, string>) =>
  useSuspenseQuery({
    queryKey: [...QUERY_KEYS.LIST, resource, JSON.stringify(params)],
    queryFn: list<T>(client, resource, params),
  })

export const useRetrieveQuery = <T>(client: APIClient, resource: string, id: string) =>
  useSuspenseQuery({
    queryKey: [...QUERY_KEYS.RETRIEVE, resource, id],
    queryFn: retrieve<T>(client, resource, id),
  })

export const useCreateMutation = <T>(client: APIClient, resource: string) =>
  useMutation({
    mutationKey: [...MUTATION_KEYS.CREATE, resource],
    mutationFn: create<T>(client, resource),
  })

export const useUpdateMutation = <T>(client: APIClient, resource: string) =>
  useMutation({
    mutationKey: [...MUTATION_KEYS.UPDATE, resource],
    mutationFn: update<T>(client, resource),
  })

export const useUpdatePreparedMutation = <T>(client: APIClient, resource: string) =>
  useMutation({
    mutationKey: [...MUTATION_KEYS.UPDATE, resource, 'prepared'],
    mutationFn: updatePrepared<T>(client, resource),
  })

export const useRemoveMutation = (client: APIClient, resource: string, id: string) =>
  useMutation({
    mutationKey: [...MUTATION_KEYS.REMOVE, resource, id],
    mutationFn: remove(client, resource, id),
  })

export const useRemovePreparedMutation = (client: APIClient, resource: string) =>
  useMutation({
    mutationKey: [...MUTATION_KEYS.REMOVE, resource, 'prepared'],
    mutationFn: removePrepared(client, resource),
  })
