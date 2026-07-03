export type GenerateInstructionRequest = {
  file: File;
};

export type GenerateInstructionResponse = {
  html_menu: string;
  html_content: string;
  ai_description: string;
};
