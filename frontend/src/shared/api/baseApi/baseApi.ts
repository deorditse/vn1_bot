import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '../middleware/auth/baseQueryWithReauth';

export const baseApiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  endpoints: () => ({}),
  tagTypes: ['USER_INFO', 'INSTRUCTION'],
});
