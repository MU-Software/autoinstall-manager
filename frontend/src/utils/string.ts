import * as R from 'remeda'

export const isFilledString = (obj: unknown): obj is string => R.isString(obj) && !R.isEmpty(obj)

// @ts-expect-error isNaN이 들어가는 순간 is string이 깨짐
export const isNumeric: (obj: unknown) => obj is string = (obj) => isFilledString(obj) && !isNaN(Number(obj))

export const isValidHttpUrl = (obj: unknown): obj is string => {
  try {
    const url = new URL(obj as string)
    return url.protocol === 'http:' || url.protocol === 'https:'
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (_) {
    return false
  }
}
