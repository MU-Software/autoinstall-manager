import cspellESLintPluginRecommended from '@cspell/eslint-plugin/recommended'
import eslint from '@eslint/js'
import importPlugin from 'eslint-plugin-import'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig } from 'eslint/config'
import globals from 'globals'
import tslint from 'typescript-eslint'

export default defineConfig(
  eslint.configs.recommended,
  tslint.configs.recommended,
  reactHooks.configs['recommended-latest'],
  reactRefresh.configs.recommended,
  jsxA11y.flatConfigs.recommended,
  eslintPluginPrettierRecommended,
  importPlugin.flatConfigs.typescript,
  {
    ...react.configs.flat.recommended,
    rules: { 'react/no-children-prop': 'off' },
  },
  {
    ...cspellESLintPluginRecommended,
    rules: { '@cspell/spellchecker': ['warn', { cspell: { words: ['rjsf', 'norender'] } }] }
  },
  {
    ignores: ['dist', 'node_modules'],
    files: ['frontend/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      globals: { ...globals.serviceworker, ...globals.browser },
      parser: tslint.parser,
      parserOptions: { project: './tsconfig.json' },
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      'react/jsx-filename-extension': [2, { extensions: ['.js', '.jsx', '.ts', '.tsx'] }],
      'sort-imports': ['error', { ignoreDeclarationSort: true }],
      'prettier/prettier': ['error', { printWidth: 150 }],
    },
  }
)
