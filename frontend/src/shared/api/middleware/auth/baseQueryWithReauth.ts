import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';

export const AUTH_REQUIRED_EVENT = 'vn1:auth-required';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_BASE_URL ?? '/auth';

const apiBaseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  credentials: 'include',
});

const authBaseQuery = fetchBaseQuery({
  baseUrl: AUTH_BASE_URL,
  credentials: 'include',
});

function isAuthRequest(args: string | FetchArgs) {
  const url = typeof args === 'string' ? args : args.url;
  return url.startsWith('/auth/');
}

function normalizeAuthArgs(args: string | FetchArgs): string | FetchArgs {
  if (typeof args === 'string') {
    return args.replace(/^\/auth/, '');
  }
  return {
    ...args,
    url: args.url.replace(/^\/auth/, ''),
  };
}

async function clearSession() {
  try {
    await fetch(`${AUTH_BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
  } finally {
    window.dispatchEvent(new Event(AUTH_REQUIRED_EVENT));
  }
}

export const baseQueryWithReauth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  const baseQuery = isAuthRequest(args) ? authBaseQuery : apiBaseQuery;
  const normalizedArgs = isAuthRequest(args) ? normalizeAuthArgs(args) : args;
  const result = await baseQuery(normalizedArgs, api, extraOptions);

  if (result.error?.status !== 401) {
    return result;
  }

  const refreshResult = await authBaseQuery(
    {
      url: '/refresh',
      method: 'POST',
    },
    api,
    extraOptions,
  );

  if (refreshResult.error) {
    await clearSession();
    return result;
  }

  const retryResult = await baseQuery(normalizedArgs, api, extraOptions);

  if (retryResult.error?.status === 401) {
    await clearSession();
  }

  return retryResult;
};
