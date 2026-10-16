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
          50: '#fdf2f8',   // softest pinkish-purple tint
          100: '#fce7f3',  // pale blush mauve
          200: '#fbcfe8',  // soft lilac pink
          300: '#f472b6',  // cheerful rose mauve
          400: '#c026d3',  // bright mauve
          500: '#a8397a',  // signature mauve / plum
          600: '#912668',  // deep plum accent
          700: '#771d54',  // rich mulberry
          800: '#5e1742',  // dark plum
          900: '#4a1234',  // deep night plum
          950: '#2f0b21',
        },
        mauve: {
          50: '#faf5f8',
          100: '#f4eaf1',
          200: '#ebd6e4',
          300: '#deb8d2',
          400: '#c992b8',
          500: '#a8397a',
          600: '#912668',
          700: '#771d54',
          800: '#5e1742',
          900: '#4a1234'
        },
        plum: {
          50: '#fdf2f8',
          100: '#fce7f3',
          200: '#fbcfe8',
          500: '#a8397a',
          600: '#912668',
          700: '#771d54',
          800: '#5e1742',
          900: '#4a1234'
        },
        wellness: {
          positive: '#10b981',
          balanced: '#a8397a',
          attention: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
