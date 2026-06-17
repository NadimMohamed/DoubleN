import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        navy:    { DEFAULT: '#0A1628', 50: '#0d1e36', 100: '#0f2240', 200: '#122236' },
        blue:    { DEFAULT: '#0364D1', light: '#1a7fe8', dark: '#0250a8' },
        emerald: { DEFAULT: '#00C48C', light: '#00d99b', dark: '#00a876' },
        danger:  { DEFAULT: '#FF4757', light: '#ff6b78' },
        slate:   { DEFAULT: '#647488', light: '#7a8ba0' },
        panel:   { DEFAULT: '#0f1f35', card: '#122236', border: '#1e3a57', hover: '#1a2f4a' },
      },
      fontFamily: { inter: ['Inter', 'system-ui', 'sans-serif'] },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0', transform: 'translateY(4px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
export default config
