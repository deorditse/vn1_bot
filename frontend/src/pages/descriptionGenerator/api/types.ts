export type GenerateDescriptionRequest =
  | {mode: 'file'; file: File}
  | {mode: 'form'; id: string; rawDescription: string};

export type GenerateDescriptionReport = {
  totalRows: number;
  errorRows: number;
  successRows: number;
};

export type GenerateDescriptionResult = {
  blob: Blob;
  report: GenerateDescriptionReport;
};
