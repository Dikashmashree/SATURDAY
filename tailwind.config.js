/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'slate': {
          900: '#0f172a',
          800: '#1e293b',
        },
        'blue': {
          900: '#1e3a8a',
          400: '#60a5fa',
          300: '#93c5fd',
        },
        'cyan': {
          400: '#22d3ee',
          300: '#67e8f9',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
} 