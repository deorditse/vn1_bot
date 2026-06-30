import { memo, Suspense, useCallback } from 'react';
import { Route, Routes } from 'react-router-dom';

import type { AppRoutesProps } from '@shared/types/router';
import { PageLoader } from '@widgets/page-loader';
import { RequireAuth } from './RequireAuth';
import { routeConfig } from './config/routeConfig';

function AppRouter() {
  const renderWithWrapper = useCallback((route: AppRoutesProps) => {
    const element = <Suspense fallback={<PageLoader />}>{route.element}</Suspense>;
    const protectedElement = route.authOnly ? <RequireAuth>{element}</RequireAuth> : element;

    if (route.index) {
      return <Route element={protectedElement} index key={`${route.path}-index`} />;
    }

    return (
      <Route element={protectedElement} key={route.path} path={normalizeNestedPath(route.path)}>
        {route.children?.map(renderWithWrapper)}
      </Route>
    );
  }, []);

  return <Routes>{Object.values(routeConfig).map(renderWithWrapper)}</Routes>;
}

function normalizeNestedPath(path: string) {
  if (path === '/') {
    return path;
  }

  return path.startsWith('/') ? path.slice(1) : path;
}

export default memo(AppRouter);
