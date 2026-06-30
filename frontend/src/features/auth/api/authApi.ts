import { baseApiSlice } from '@shared/api/baseApi/baseApi';

import type { AuthResponse, LoginRequest, UserProfile } from './types';

export const authApi = baseApiSlice.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (body) => ({
        url: '/auth/login',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['USER_INFO'],
    }),
    logout: builder.mutation<AuthResponse, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
      invalidatesTags: ['USER_INFO'],
    }),
    getMe: builder.query<UserProfile, void>({
      query: () => '/auth/me',
      providesTags: ['USER_INFO'],
    }),
  }),
});

export const { useGetMeQuery, useLazyGetMeQuery, useLoginMutation, useLogoutMutation } = authApi;
