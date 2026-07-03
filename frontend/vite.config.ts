import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite serves the renderer at http://localhost:5173 in dev.
// Electron loads that URL when COPILOT_DEV=1, otherwise loads dist/index.html.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { port: 5174, strictPort: true },
  build: { outDir: "dist", emptyOutDir: true },
});
