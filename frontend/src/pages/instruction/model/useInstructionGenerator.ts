import {useMemo, useState} from 'react';

import type {GenerateInstructionResponse} from '../api/types';
import {
  useGenerateAiDescriptionMutation,
  useGenerateInstructionMutation,
  useUploadInstructionFileMutation,
} from '../api/instructionApi';
import {buildInstructionBlocks} from '../lib/buildInstructionBlocks';
import type {GenerationOptions} from './types';

const GENERATION_OPTIONS_STORAGE_KEY = 'vn1:generation-options';

const DEFAULT_GENERATION_OPTIONS: GenerationOptions = {
  instruction: true,
  aiDescription: false,
};

function getStoredGenerationOptions(): GenerationOptions {
  try {
    const value = window.localStorage.getItem(GENERATION_OPTIONS_STORAGE_KEY);

    if (!value) {
      return DEFAULT_GENERATION_OPTIONS;
    }

    return {
      ...DEFAULT_GENERATION_OPTIONS,
      ...JSON.parse(value),
    };
  } catch {
    return DEFAULT_GENERATION_OPTIONS;
  }
}

function getGenerationErrorMessage(err: unknown, fallback: string) {
  if (typeof err !== 'object' || err === null) {
    return fallback;
  }

  if ('status' in err && err.status === 'FETCH_ERROR') {
    return `Backend недоступен. Проверьте, что API доступен по ${__API_BASE_URL__}`;
  }

  if ('error' in err && typeof err.error === 'string') {
    if (err.error.includes('Failed to fetch') || err.error.includes('ECONNREFUSED')) {
      return `Backend недоступен. Проверьте, что API доступен по ${__API_BASE_URL__}`;
    }
  }

  if ('data' in err && typeof err.data === 'object' && err.data !== null && 'detail' in err.data) {
    const detail = err.data.detail;

    if (typeof detail === 'string') {
      return detail;
    }
  }

  if (err instanceof Error) {
    return err.message;
  }

  return fallback;
}

export function useInstructionGenerator() {
  const [file, setFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [instruction, setInstruction] = useState<GenerateInstructionResponse | null>(null);
  const [aiDescription, setAiDescription] = useState<string>('');
  const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
  const [generationOptions, setGenerationOptions] = useState<GenerationOptions>(getStoredGenerationOptions);
  const [uploadInstructionFile, {isLoading: isFileUploading}] = useUploadInstructionFileMutation();
  const [generateInstruction, {isLoading: isInstructionLoading}] = useGenerateInstructionMutation();
  const [generateAiDescription, {isLoading: isAiDescriptionLoading}] = useGenerateAiDescriptionMutation();
  const isLoading = isFileUploading || isInstructionLoading || isAiDescriptionLoading;

  const markupBlocks = useMemo(() => buildInstructionBlocks(instruction), [instruction]);

  const selectFile = (nextFile: File) => {
    setFile(nextFile);
    setFileId(null);
    setError(null);
    setInstruction(null);
    setAiDescription('');
    setCopiedBlock(null);
  };

  const resetInstruction = () => {
    setFile(null);
    setFileId(null);
    setError(null);
    setInstruction(null);
    setAiDescription('');
    setCopiedBlock(null);
  };

  const removeSelectedFile = () => {
    setFile(null);
    setFileId(null);
    setError(null);
    setCopiedBlock(null);
  };

  const updateGenerationOptions = (nextOptions: GenerationOptions) => {
    setGenerationOptions(nextOptions);
    window.localStorage.setItem(GENERATION_OPTIONS_STORAGE_KEY, JSON.stringify(nextOptions));
  };

  const ensureFileUploaded = async () => {
    if (fileId) {
      return fileId;
    }

    if (!file) {
      throw new Error('Выберите DOCX-файл');
    }

    const result = await uploadInstructionFile({file}).unwrap();
    setFileId(result.file_id);

    return result.file_id;
  };

  const convert = async () => {
    if (!file) {
      setError('Выберите DOCX-файл');
      return;
    }

    if (!generationOptions.instruction && !generationOptions.aiDescription) {
      setError('Выберите, что нужно сгенерировать');
      return;
    }

    setError(null);
    setCopiedBlock(null);

    if (generationOptions.instruction) {
      setInstruction(null);
    }

    if (generationOptions.aiDescription) {
      setAiDescription('');
    }

    try {
      const uploadedFileId = await ensureFileUploaded();

      if (generationOptions.instruction) {
        const result = await generateInstruction({fileId: uploadedFileId}).unwrap();
        setInstruction(result);
      }

      if (generationOptions.aiDescription) {
        const result = await generateAiDescription({fileId: uploadedFileId}).unwrap();
        setAiDescription(result.description);
      }
    } catch (err) {
      setError(getGenerationErrorMessage(err, 'Не удалось выполнить генерацию'));
    }
  };

  const generateDescriptionOnly = async () => {
    if (!file) {
      setError('Выберите DOCX-файл');
      return;
    }

    setError(null);
    setCopiedBlock(null);
    setAiDescription('');

    try {
      const uploadedFileId = await ensureFileUploaded();
      const result = await generateAiDescription({fileId: uploadedFileId}).unwrap();
      setAiDescription(result.description);
    } catch (err) {
      setError(getGenerationErrorMessage(err, 'Не удалось сформировать ИИ-описание'));
    }
  };

  const copyText = async (key: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedBlock(key);
    window.setTimeout(() => setCopiedBlock(null), 1600);
  };

  return {
    aiDescription,
    copiedBlock,
    error,
    file,
    fileId,
    generationOptions,
    instruction,
    isAiDescriptionLoading,
    isFileUploading,
    isInstructionLoading,
    isLoading,
    markupBlocks,
    convert,
    copyText,
    generateDescriptionOnly,
    removeSelectedFile,
    resetInstruction,
    selectFile,
    updateGenerationOptions,
  };
}
