export type InstructionBlock = {
  key: string;
  title: string;
  content: string;
};

export type CopyTextHandler = (key: string, content: string) => Promise<void>;

export type AiDescriptionProductType = 'medicine' | 'non_medicine';

export type NonMedicineCategory = 'dietary_supplement' | 'medical_nutrition' | 'medical_device' | 'hygiene' | 'cosmetics';

export type GenerationOptions = {
  instruction: boolean;
  aiDescription: boolean;
  aiDescriptionProductType: AiDescriptionProductType;
  nonMedicineCategory: NonMedicineCategory;
};
