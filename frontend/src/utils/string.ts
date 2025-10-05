import * as R from 'remeda'

export const UUID_REGEX = /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i

export const isFilledString = (obj: unknown): obj is string => R.isString(obj) && !R.isEmpty(obj)

export const isUUID = (obj: unknown): obj is string => R.isString(obj) && UUID_REGEX.test(obj)

export const isValidHttpUrl = (obj: unknown): obj is string => {
  try {
    const url = new URL(obj as string)
    return url.protocol === 'http:' || url.protocol === 'https:'
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (_) {
    return false
  }
}
