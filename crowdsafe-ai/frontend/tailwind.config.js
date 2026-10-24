/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0F17',
          850: '#101622',
          800: '#161F30',
          750: '#1C273C',
          700: '#23324D',
          600: '#334155'
        },
        risk: {
          normal: '#10B981',     // emerald-500
          increasing: '#F59E0B', // amber-500
          high: '#F97316',       // orange-500
          critical: '#EF4444'    // red-500
        }
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      }
    },
  },
  plugins: [],
}
