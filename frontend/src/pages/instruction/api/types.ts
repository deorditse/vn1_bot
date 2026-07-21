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

export type AiDescriptionProductType = 'medicine' | 'non_medicine';

export type NonMedicineCategory = 'dietary_supplement' | 'medical_nutrition' | 'medical_device' | 'hygiene' | 'cosmetics';

export type GenerateAiDescriptionRequest = {
  fileId: string;
  productType: AiDescriptionProductType;
  nonMedicineCategory?: NonMedicineCategory;
};

export type GenerateAiDescriptionResponse = {
  description: string;
};
