import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Dev-server proxy so `npm run dev` can talk to a locally running FastAPI
// backend without CORS setup; the production build is served BY FastAPI
// itself (see backend/main.py StaticFiles mount), so no proxy exists there.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8090",
    },
  },
  build: {
    outDir: "dist",
  },
});
