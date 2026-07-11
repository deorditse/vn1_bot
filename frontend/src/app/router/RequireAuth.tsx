import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useAuth } from '@features/auth';
import { PageLoader } from '@widgets/page-loader';
import { getRouteLogin } from '@shared/const/router';

type Props = {
  children: ReactNode;
};

const isDevAuthDisabled = import.meta.env.DEV;

export function RequireAuth({ children }: Props) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isDevAuthDisabled) {
    return <>{children}</>;
  }

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to={getRouteLogin()} />;
  }

  return <>{children}</>;
}
