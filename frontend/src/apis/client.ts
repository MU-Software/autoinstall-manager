import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import axios from 'axios'
import * as R from 'remeda'

import type { ErrorResponseSchema } from '@frontend/schemas/api'
import { isObjectErrorResponseSchema } from '@frontend/utils/api'

const DEFAULT_ERROR_CODE = -1
const DEFAULT_ERROR_MESSAGE = '알 수 없는 문제가 발생했습니다, 잠시 후 다시 시도해주세요.'
const DEFAULT_ERROR_RESPONSE = {
  type: 'unknown',
  errors: [{ code: 'unknown', detail: DEFAULT_ERROR_MESSAGE, attr: null }],
}

export class APIClientError extends Error {
  readonly name = 'APIClientError'
  readonly status: number
  readonly detail: ErrorResponseSchema
  readonly originalError: unknown

  constructor(error?: unknown) {
    let status: number = DEFAULT_ERROR_CODE
    let message: string = DEFAULT_ERROR_MESSAGE
    let detail: ErrorResponseSchema = DEFAULT_ERROR_RESPONSE

    if (axios.isAxiosError(error)) {
      const response = error.response

      if (response) {
        status = response.status
        detail = isObjectErrorResponseSchema(response.data)
          ? response.data
          : {
              type: 'axios_error',
              errors: [
                {
                  code: 'unknown',
                  detail: R.isString(response.data) ? response.data : DEFAULT_ERROR_MESSAGE,
                  attr: null,
                },
              ],
            }
        message = detail.errors[0].detail || DEFAULT_ERROR_MESSAGE
      }
    } else if (error instanceof Error) {
      message = error.message
      detail = {
        type: error.name || typeof error || 'unknown',
        errors: [{ code: 'unknown', detail: error.message, attr: null }],
      }
    }

    super(message)
    this.originalError = error || null
    this.status = status
    this.detail = detail
  }

  isRequiredAuth(): boolean {
    return this.status === 401 || this.status === 403
  }
}

type AxiosRequestWithoutPayload = <T = unknown, R = AxiosResponse<T>, D = unknown>(url: string, config?: AxiosRequestConfig<D>) => Promise<R>
type AxiosRequestWithPayload = <T = unknown, R = AxiosResponse<T>, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>) => Promise<R>

export class APIClient {
  readonly baseURL: string
  private readonly API: AxiosInstance

  constructor(baseURL: string, timeout: number) {
    const headers = { 'Content-Type': 'application/json' }
    this.baseURL = baseURL
    this.API = axios.create({ baseURL, timeout, headers })
  }

  _safe_request_without_payload(requestFunc: AxiosRequestWithoutPayload): AxiosRequestWithoutPayload {
    return async <T = unknown, R = AxiosResponse<T>, D = unknown>(url: string, config?: AxiosRequestConfig<D>) => {
      try {
        return await requestFunc<T, R, D>(url, config)
      } catch (error) {
        throw new APIClientError(error)
      }
    }
  }

  _safe_request_with_payload(requestFunc: AxiosRequestWithPayload): AxiosRequestWithPayload {
    return async <T = unknown, R = AxiosResponse<T>, D = unknown>(url: string, data: D, config?: AxiosRequestConfig<D>) => {
      try {
        return await requestFunc<T, R, D>(url, data, config)
      } catch (error) {
        throw new APIClientError(error)
      }
    }
  }

  async get<T, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T> {
    return (await this._safe_request_without_payload(this.API.get)<T, AxiosResponse<T>, D>(url, config)).data
  }
  async post<T, D>(url: string, data: D, config?: AxiosRequestConfig<D>): Promise<T> {
    return (await this._safe_request_with_payload(this.API.post)<T, AxiosResponse<T>, D>(url, data, config)).data
  }
  async put<T, D>(url: string, data: D, config?: AxiosRequestConfig<D>): Promise<T> {
    return (await this._safe_request_with_payload(this.API.put)<T, AxiosResponse<T>, D>(url, data, config)).data
  }
  async patch<T, D>(url: string, data: D, config?: AxiosRequestConfig<D>): Promise<T> {
    return (await this._safe_request_with_payload(this.API.patch)<T, AxiosResponse<T>, D>(url, data, config)).data
  }
  async delete<T, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T> {
    return (await this._safe_request_without_payload(this.API.delete)<T, AxiosResponse<T>, D>(url, config)).data
  }
}
