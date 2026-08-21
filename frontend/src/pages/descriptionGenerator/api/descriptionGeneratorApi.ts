import {baseApiSlice} from '@shared/api';
import type {GenerateDescriptionRequest} from './types';

const XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

export const descriptionGeneratorApi = baseApiSlice.injectEndpoints({
  endpoints: (builder) => ({
    generateDescription: builder.mutation<Blob, GenerateDescriptionRequest>({
      query: (request) => {
        if (request.mode === 'file') {
          const body = new FormData();
          body.append('file', request.file);
          return {
            url: '/generate-description',
            method: 'POST',
            body,
            responseHandler: async (response: Response) =>
              response.headers.get('content-type')?.includes(XLSX_CONTENT_TYPE)
                ? response.blob()
                : response.json(),
          };
        }

        return {
          url: '/generate-description',
          method: 'POST',
          body: {
            id: request.id,
            raw_description: request.rawDescription,
          },
          responseHandler: async (response: Response) =>
            response.headers.get('content-type')?.includes(XLSX_CONTENT_TYPE)
              ? response.blob()
              : response.json(),
        };
      },
    }),
  }),
});

export const {useGenerateDescriptionMutation} = descriptionGeneratorApi;
