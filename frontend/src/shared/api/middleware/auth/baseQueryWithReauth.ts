import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';

export const AUTH_REQUIRED_EVENT = 'vn1:auth-required';

const apiBaseQuery = fetchBaseQuery({
  baseUrl: __API_BASE_URL__,
  credentials: 'include',
});

const generatorApiBaseQuery = fetchBaseQuery({
  baseUrl: __GENERATOR_API_BASE_URL__,
  credentials: 'include',
});

const authBaseQuery = fetchBaseQuery({
  baseUrl: __AUTH_BASE_URL__,
  credentials: 'include',
});

function isAuthRequest(args: string | FetchArgs) {
  const url = typeof args === 'string' ? args : args.url;
  return url.startsWith('/auth/');
}

function isGeneratorRequest(args: string | FetchArgs) {
  const url = typeof args === 'string' ? args : args.url;
  return url.startsWith('/generate/');
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
    await fetch(`${__AUTH_BASE_URL__}/logout`, {
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
  const baseQuery = isAuthRequest(args)
    ? authBaseQuery
    : isGeneratorRequest(args)
      ? generatorApiBaseQuery
      : apiBaseQuery;
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
