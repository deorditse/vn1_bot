import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider } from 'antd';
import { BrowserRouter } from 'react-router-dom';

import AppRouter from './router/AppRouter';
import { AuthProvider } from '@features/auth';
import { StoreProvider } from './providers/StoreProvider';
import { appTheme, applyAppDesignTokens } from './styles/theme';
import 'antd/dist/reset.css';
import './styles/global.less';

applyAppDesignTokens();

createRoot(document.getElementById('root') as HTMLElement).render(
  <StrictMode>
    <ConfigProvider theme={appTheme}>
      <StoreProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppRouter />
          </AuthProvider>
        </BrowserRouter>
      </StoreProvider>
    </ConfigProvider>
  </StrictMode>,
);
