export type GenerateInstructionRequest = {
  file: File;
};

export type GenerateInstructionResponse = {
  html_menu: string;
  html_content: string;
  ai_description: string;
};

export type GenerateShortDescriptionRequest = {
  markdown: string;
  dispensing?: string;
};

export type GenerateShortDescriptionResponse = {
  description: string;
};
