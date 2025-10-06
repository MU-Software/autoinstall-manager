import '@fontsource/pretendard'
import '@fontsource/ubuntu'
import '@fontsource/ubuntu-mono'

import { createTheme } from '@mui/material/styles'

const CANONICAL_ORANGE_COLOR_PALETTE: Record<number, string> = {
  900: '#b43b10',
  800: '#cd4717',
  700: '#db4e1a',
  600: '#e9551f', // primary
  500: '#f45b23',
  400: '#f57243',
  300: '#f68b65',
  200: '#f9ab91',
  100: '#fbccbc',
  50: '#f9e9e7',
}
const CANONICAL_ORANGE_SCHEME = {
  dark: CANONICAL_ORANGE_COLOR_PALETTE[900], // or use #a33b15
  main: CANONICAL_ORANGE_COLOR_PALETTE[600], // primary
  light: CANONICAL_ORANGE_COLOR_PALETTE[300], // or use #ed774b
  contrastText: '#fff',
}

export const canonicalTheme = createTheme({
  palette: { primary: CANONICAL_ORANGE_SCHEME },
  typography: {
    fontFamily: [
      'Ubuntu',
      'Ubuntu Mono',
      // eslint-disable-next-line @cspell/spellchecker
      'Pretendard',
      '-apple-system',
      'BlinkMacSystemFont',
      'system-ui',
      'Roboto',
      // eslint-disable-next-line @cspell/spellchecker
      'Helvetica Neue',
      // eslint-disable-next-line @cspell/spellchecker
      'Segoe UI',
      'Apple SD Gothic Neo',
      // eslint-disable-next-line @cspell/spellchecker
      'Noto Sans KR',
      // eslint-disable-next-line @cspell/spellchecker
      'Malgun Gothic',
      'Apple Color Emoji',
      // eslint-disable-next-line @cspell/spellchecker
      'Segoe UI Emoji',
      // eslint-disable-next-line @cspell/spellchecker
      'Segoe UI Symbol',
      'sans-serif',
    ]
      .map((f) => `"${f}"`)
      .join(','),
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        'html, body': {
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
          WebkitTouchCallout: 'none',

          overscrollBehavior: 'none',
          wordBreak: 'keep-all',
          overflowWrap: 'break-word',

          WebkitUserDrag: 'none',
          // eslint-disable-next-line @cspell/spellchecker
          KhtmlUserDrag: 'none',
          MozUserDrag: 'none',
          OUserDrag: 'none',
          userDrag: 'none',

          // eslint-disable-next-line @cspell/spellchecker
          fontVariantNumeric: 'tabular-nums',
        },
        a: { textDecoration: 'none' },
      },
    },
    MuiTableCell: { styleOverrides: { root: { borderBottom: 'none' } } },
  },
})
