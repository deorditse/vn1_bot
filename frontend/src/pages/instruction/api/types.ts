export type UploadInstructionFileRequest = {
  file: File;
};

export type UploadInstructionFileResponse = {
  file_id: string;
  file_name: string;
};

export type GenerateInstructionRequest = {
  fileId: string;
};

export type GenerateInstructionResponse = {
  html_menu: string;
  html_content: string;
};

export type GenerateAiDescriptionRequest = {
  fileId: string;
};

export type GenerateAiDescriptionResponse = {
  description: string;
};
