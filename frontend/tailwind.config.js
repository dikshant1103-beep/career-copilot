/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b0f17",
        panel: "#121826",
        panel2: "#1a2233",
        line: "#27314a",
        accent: "#5eead4",
        accent2: "#a78bfa",
      },
    },
  },
  plugins: [],
};
