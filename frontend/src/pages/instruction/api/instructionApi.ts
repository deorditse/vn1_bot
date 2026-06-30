import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from '@shared/api/middleware/auth/baseQueryWithReauth';
import type {
  GenerateInstructionRequest,
  GenerateInstructionResponse,
  GenerateShortDescriptionRequest,
  GenerateShortDescriptionResponse,
} from './types';

export const instructionApi = createApi({
  reducerPath: 'instructionApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['INSTRUCTION'],
  endpoints: (builder) => ({
    generateInstruction: builder.mutation<GenerateInstructionResponse, GenerateInstructionRequest>({
      query: ({ file }) => {
        const formData = new FormData();
        formData.append('file', file);

        return {
          url: '/generate/instruction',
          method: 'POST',
          body: formData,
        };
      },
    }),
    generateShortDescription: builder.mutation<GenerateShortDescriptionResponse, GenerateShortDescriptionRequest>({
      query: ({ markdown, dispensing = 'По рецепту' }) => ({
        url: '/generate/short-description',
        method: 'POST',
        body: {
          markdown,
          dispensing,
        },
      }),
    }),
  }),
});

export const { useGenerateInstructionMutation, useGenerateShortDescriptionMutation } = instructionApi;
