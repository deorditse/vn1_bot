import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@shared/api/middleware/auth/baseQueryWithReauth';
import type { GenerateInstructionRequest } from './types';

export const instructionApi = createApi({
  reducerPath: 'instructionApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['INSTRUCTION'],
  endpoints: (builder) => ({
    generateInstruction: builder.mutation<Blob, GenerateInstructionRequest>({
      query: ({ file }) => {
        const formData = new FormData();
        formData.append('file', file);

        return {
          url: '/generate/instruction',
          method: 'POST',
          body: formData,
          responseHandler: (response) => response.blob(),
        };
      },
    }),
  }),
});

export const { useGenerateInstructionMutation } = instructionApi;
