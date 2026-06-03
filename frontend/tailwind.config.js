/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        zendesk: {
          green: "#0b192c",
          lightGreen: "#10b981",
          accent: "#ff6d4a",
          dark: "#020617",
          muted: "#94a3b8",
          bg: "#020617",
          card: "rgba(255, 255, 255, 0.03)",
          text: "#f8fafc",
          border: "rgba(255, 255, 255, 0.08)",
        }
      }
    },
  },
  plugins: [],
}
