import { lazy } from 'react';

export const LoginPageAsync = lazy(() =>
  import('./LoginPage').then((module) => ({ default: module.LoginPage })),
);
