/// <reference types="vite/client" />
interface ViteTypeOptions {
  strictImportEnv: unknown
}

interface ImportMetaEnv {
  readonly VITE_API_DOMAIN: string
  readonly VITE_API_TIMEOUT: number
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
