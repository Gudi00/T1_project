/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",
        secondary: "#3B82F6",
        accent: "#93C5FD",
        background: "#0F172A"
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
}
