import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: { alias: [{ find: /^@\//, replacement: '/src/' }] },
  server: { port: 5174, strictPort: true },
  preview: { port: 5174, strictPort: true },
});
