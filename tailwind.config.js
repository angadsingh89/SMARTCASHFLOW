/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#edf5ff",
          500: "#1f5ed9",
          700: "#183ea8"
        }
      }
    }
  },
  plugins: []
};
