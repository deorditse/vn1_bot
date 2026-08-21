export type GenerateDescriptionRequest =
  | {mode: 'file'; file: File}
  | {mode: 'form'; id: string; rawDescription: string};
