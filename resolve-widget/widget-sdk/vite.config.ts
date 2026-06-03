import { defineConfig } from "vite";

export default defineConfig({
  build: {
    lib: {
      entry: "src/main.ts",
      name: "ResolveAISDK",
      fileName: () => "sdk",
      formats: ["iife"],
    },

    rollupOptions: {
      output: {
        assetFileNames: "sdk.css",
      },
    },
  },
});
