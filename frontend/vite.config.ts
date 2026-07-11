import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig(({ mode }) => {
  const env = {
    ...loadEnv('example', process.cwd(), ''),
    ...loadEnv(mode, process.cwd(), ''),
  };
  const plugins = [react()];
  const clientEnv = {
    __API_BASE_URL__: JSON.stringify(env.API_BASE_URL),
    __AUTH_BASE_URL__: JSON.stringify(env.AUTH_BASE_URL),
  };

  return {
    plugins,
    resolve: {
      alias: {
        '@app': path.resolve(__dirname, 'src/app'),
        '@pages': path.resolve(__dirname, 'src/pages'),
        '@features': path.resolve(__dirname, 'src/features'),
        '@widgets': path.resolve(__dirname, 'src/widgets'),
        '@shared': path.resolve(__dirname, 'src/shared'),
      },
    },
    define: {
      ...clientEnv,
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: env.DEV_PROXY_API_TARGET,
          changeOrigin: true,
          secure: false,
          rewrite: (url) => url.replace(/^\/api/, ''),
        },
        '/auth': {
          target: env.DEV_PROXY_AUTH_TARGET,
          changeOrigin: true,
          secure: false,
          rewrite: (url) => url.replace(/^\/auth/, '/v1/auth'),
        },
      },
    },
  };
});
