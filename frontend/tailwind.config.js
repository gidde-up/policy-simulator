/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'wb-blue': '#002244',
        'wb-light': '#009FDA',
        'zaf-green': '#007749',
        'zaf-gold': '#FFB81C',
        'tun-red': '#E70013',
      }
    },
  },
  plugins: [],
}
