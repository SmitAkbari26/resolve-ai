import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ["https://be47-14-98-189-6.ngrok-free.app"],
    port: 5176,
  },
});
