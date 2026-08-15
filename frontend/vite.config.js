import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// TODO: proxy /api to the backend in dev instead of hardcoding the base URL
// in src/api/client.js, once we finalize deployment (single origin vs split).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
