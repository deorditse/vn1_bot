import {baseApiSlice} from '@shared/api';
import type {
    GenerateInstructionRequest,
    GenerateInstructionResponse,
} from './types';

export const instructionApi = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        generateInstruction: builder.mutation<GenerateInstructionResponse, GenerateInstructionRequest>({
            query: ({file}) => {
                const formData = new FormData();
                formData.append('file', file);

                return {
                    url: '/generate/instruction',
                    method: 'POST',
                    body: formData,
                };
            },
            invalidatesTags: ['INSTRUCTION'],
        }),
    }),
});

export const {useGenerateInstructionMutation} = instructionApi;
