import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/tests/**/*.test.ts"],
    setupFiles: ["src/tests/setup.ts"],
  },
});
