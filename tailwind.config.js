/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#FDF3F0',
          100: '#FBE4DF',
          200: '#F7C9BE',
          300: '#F1A594',
          400: '#E87A63',
          500: '#D94826', // Terracota patrimonial Evenjoy
          600: '#B83515',
          700: '#942B12',
          800: '#752512',
          900: '#5F2213',
        },
        sand: {
          50: '#FAF9F6', // Neutral canvas editorial
          100: '#F5F3ED',
          200: '#EBE7DC',
          300: '#DDD6C5',
          400: '#C9BEA7',
          500: '#B0A288',
        },
        forest: {
          50: '#F0F5F2',
          100: '#DFEAE3',
          200: '#C1D5C9',
          500: '#2A5C45',
          700: '#1E4636', // Verde montaña antioqueña
          900: '#122B21',
        },
        warm: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          500: '#F59E0B',
          600: '#D97706',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 8px -1px rgba(0, 0, 0, 0.05), 0 1px 3px -1px rgba(0, 0, 0, 0.03)',
        'card-hover': '0 12px 28px -4px rgba(0, 0, 0, 0.09), 0 4px 10px -2px rgba(0, 0, 0, 0.04)',
        'sheet': '0 -10px 40px -10px rgba(0, 0, 0, 0.15)',
        'float': '0 10px 30px -5px rgba(217, 72, 38, 0.25)',
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
        '4xl': '32px',
      },
      transitionTimingFunction: {
        'natural': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
