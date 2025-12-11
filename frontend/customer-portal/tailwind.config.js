/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d4ff',
          300: '#a4b5ff',
          400: '#7d8dff',
          500: '#4472c4',
          600: '#3d5fa8',
          700: '#324c8c',
          800: '#2a3f70',
          900: '#253359'
        },
        secondary: {
          50: '#f0f7f0',
          100: '#d4edda',
          200: '#a9dba9',
          300: '#70ad47',
          400: '#569f35',
          500: '#469028',
          600: '#38721f',
          700: '#2a5519',
          800: '#1f3d12',
          900: '#142a0c'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        card: '0 2px 8px rgba(0, 0, 0, 0.1)'
      },
      spacing: {
        safe: 'max(1rem, env(safe-area-inset-bottom))',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
