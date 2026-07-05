import {baseApiSlice} from '@shared/api';
import type {
    GenerateAiDescriptionRequest,
    GenerateAiDescriptionResponse,
    GenerateInstructionRequest,
    GenerateInstructionResponse,
    UploadInstructionFileRequest,
    UploadInstructionFileResponse,
} from './types';

export const instructionApi = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        uploadInstructionFile: builder.mutation<UploadInstructionFileResponse, UploadInstructionFileRequest>({
            query: ({file}) => {
                const formData = new FormData();
                formData.append('file', file);

                return {
                    url: '/generate/file',
                    method: 'POST',
                    body: formData,
                };
            },
            invalidatesTags: ['INSTRUCTION'],
        }),
        generateInstruction: builder.mutation<GenerateInstructionResponse, GenerateInstructionRequest>({
            query: ({fileId}) => ({
                url: '/generate/instruction',
                method: 'POST',
                body: {
                    file_id: fileId,
                },
            }),
            invalidatesTags: ['INSTRUCTION'],
        }),
        generateAiDescription: builder.mutation<GenerateAiDescriptionResponse, GenerateAiDescriptionRequest>({
            query: ({fileId}) => ({
                url: '/generate/ai_short_description',
                method: 'POST',
                body: {
                    file_id: fileId,
                },
            }),
            invalidatesTags: ['INSTRUCTION'],
        }),
    }),
});

export const {useGenerateAiDescriptionMutation, useGenerateInstructionMutation, useUploadInstructionFileMutation} = instructionApi;
