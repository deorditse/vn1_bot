import {baseApiSlice} from '@shared/api';
import type {GenerateDescriptionRequest, GenerateDescriptionResult} from './types';

const XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

const parseCountHeader = (response: Response, name: string) => {
  const value = Number(response.headers.get(name) ?? 0);
  return Number.isFinite(value) && value >= 0 ? value : 0;
};

const responseHandler = async (response: Response) => {
  if (!response.headers.get('content-type')?.includes(XLSX_CONTENT_TYPE)) {
    return response.json();
  }

  return {
    blob: await response.blob(),
    report: {
      totalRows: parseCountHeader(response, 'x-vn1-total-rows'),
      errorRows: parseCountHeader(response, 'x-vn1-error-rows'),
      successRows: parseCountHeader(response, 'x-vn1-success-rows'),
    },
  } satisfies GenerateDescriptionResult;
};

export const descriptionGeneratorApi = baseApiSlice.injectEndpoints({
  endpoints: (builder) => ({
    generateDescription: builder.mutation<GenerateDescriptionResult, GenerateDescriptionRequest>({
      query: (request) => {
        if (request.mode === 'file') {
          const body = new FormData();
          body.append('file', request.file);
          return {
            url: '/generate-description',
            method: 'POST',
            body,
            responseHandler,
          };
        }

        return {
          url: '/generate-description',
          method: 'POST',
          body: {
            id: request.id,
            raw_description: request.rawDescription,
          },
          responseHandler,
        };
      },
    }),
  }),
});

export const {useGenerateDescriptionMutation} = descriptionGeneratorApi;
