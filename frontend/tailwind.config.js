/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: '#07131e',
        panel: '#102432',
      },
      keyframes: {
        pulseSlow: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%': { opacity: 0.8, transform: 'scale(1.03)' },
        },
      },
      animation: {
        pulseSlow: 'pulseSlow 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
