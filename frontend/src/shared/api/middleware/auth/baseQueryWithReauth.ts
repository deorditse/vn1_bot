import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';

export const AUTH_REQUIRED_EVENT = 'vn1:auth-required';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

const baseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  credentials: 'include',
});

async function clearSession() {
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, {
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
  const result = await baseQuery(args, api, extraOptions);

  if (result.error?.status !== 401) {
    return result;
  }

  const refreshResult = await baseQuery(
    {
      url: '/auth/refresh',
      method: 'POST',
    },
    api,
    extraOptions,
  );

  if (refreshResult.error) {
    await clearSession();
    return result;
  }

  const retryResult = await baseQuery(args, api, extraOptions);

  if (retryResult.error?.status === 401) {
    await clearSession();
  }

  return retryResult;
};
