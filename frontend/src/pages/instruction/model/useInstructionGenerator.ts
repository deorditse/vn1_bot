import {useMemo, useRef, useState} from 'react';

import type {GenerateInstructionResponse} from '../api/types';
import {
  useGenerateAiDescriptionMutation,
  useGenerateInstructionMutation,
  useUploadInstructionFileMutation,
} from '../api/instructionApi';
import {buildInstructionBlocks} from '../lib/buildInstructionBlocks';
import type {GenerationOptions, InstructionInputMode} from './types';

const GENERATION_OPTIONS_STORAGE_KEY = 'vn1:generation-options';
const INPUT_MODE_STORAGE_KEY = 'vn1:instruction-input-mode';

type AbortableRequest<T> = {
  abort: () => void;
  unwrap: () => Promise<T>;
};

const DEFAULT_GENERATION_OPTIONS: GenerationOptions = {
  instruction: true,
  aiDescription: true,
  aiDescriptionProductType: 'medicine',
  nonMedicineCategory: 'dietary_supplement',
};

function getStoredGenerationOptions(): GenerationOptions {
  try {
    const value = window.localStorage.getItem(GENERATION_OPTIONS_STORAGE_KEY);

    if (!value) {
      return DEFAULT_GENERATION_OPTIONS;
    }

    const stored = {
      ...DEFAULT_GENERATION_OPTIONS,
      ...JSON.parse(value),
    };
    return !stored.instruction && !stored.aiDescription
      ? DEFAULT_GENERATION_OPTIONS
      : stored;
  } catch {
    return DEFAULT_GENERATION_OPTIONS;
  }
}

function getStoredInputMode(): InstructionInputMode {
  try {
    const value = window.localStorage.getItem(INPUT_MODE_STORAGE_KEY);
    return value === 'text' || value === 'file' ? value : 'file';
  } catch {
    return 'file';
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

  if ('data' in err && typeof err.data === 'object' && err.data !== null && 'error' in err.data) {
    const error = err.data.error;

    if (typeof error === 'object' && error !== null && 'message' in error && typeof error.message === 'string') {
      return error.message;
    }
  }

  if (err instanceof Error) {
    return err.message;
  }

  return fallback;
}

export function useInstructionGenerator() {
  const [inputMode, setInputMode] = useState<InstructionInputMode>(getStoredInputMode);
  const [file, setFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [instructionText, setInstructionText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [instruction, setInstruction] = useState<GenerateInstructionResponse | null>(null);
  const [aiDescription, setAiDescription] = useState<string>('');
  const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
  const [generationOptions, setGenerationOptions] = useState<GenerationOptions>(getStoredGenerationOptions);
  const [uploadInstructionFile, {isLoading: isFileUploading}] = useUploadInstructionFileMutation();
  const [generateInstruction, {isLoading: isInstructionLoading}] = useGenerateInstructionMutation();
  const [generateAiDescription, {isLoading: isAiDescriptionLoading}] = useGenerateAiDescriptionMutation();
  const isLoading = isFileUploading || isInstructionLoading || isAiDescriptionLoading;
  const activeRequestRef = useRef<AbortableRequest<unknown> | null>(null);
  const cancelRequestedRef = useRef(false);

  const markupBlocks = useMemo(() => buildInstructionBlocks(instruction), [instruction]);
  const hasInstructionSource = inputMode === 'file' ? Boolean(file) : Boolean(instructionText.trim());

  const selectFile = (nextFile: File) => {
    setInputMode('file');
    window.localStorage.setItem(INPUT_MODE_STORAGE_KEY, 'file');
    setFile(nextFile);
    setFileId(null);
    setError(null);
    setInstruction(null);
    setAiDescription('');
    setCopiedBlock(null);
  };

  const selectInputMode = (nextMode: InstructionInputMode) => {
    setInputMode(nextMode);
    window.localStorage.setItem(INPUT_MODE_STORAGE_KEY, nextMode);
    setError(null);
    setCopiedBlock(null);

    if (nextMode === 'text') {
      setFile(null);
      setFileId(null);
      setGenerationOptions((currentOptions) => {
        const nextOptions = {
          ...currentOptions,
          instruction: false,
          aiDescription: true,
        };
        window.localStorage.setItem(GENERATION_OPTIONS_STORAGE_KEY, JSON.stringify(nextOptions));
        return nextOptions;
      });
    }
  };

  const updateInstructionText = (value: string) => {
    setInstructionText(value);
    setFile(null);
    setFileId(null);
    setError(null);
    setInstruction(null);
    setAiDescription('');
    setCopiedBlock(null);
  };

  const resetInstruction = () => {
    setFile(null);
    setFileId(null);
    setInstructionText('');
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
    const normalizedOptions = inputMode === 'text'
      ? {
          ...nextOptions,
          instruction: false,
          aiDescription: true,
        }
      : nextOptions;
    setGenerationOptions(normalizedOptions);
    window.localStorage.setItem(GENERATION_OPTIONS_STORAGE_KEY, JSON.stringify(normalizedOptions));
  };

  const trackRequest = async <T,>(request: AbortableRequest<T>): Promise<T> => {
    activeRequestRef.current = request as AbortableRequest<unknown>;
    try {
      return await request.unwrap();
    } finally {
      if (activeRequestRef.current === request) {
        activeRequestRef.current = null;
      }
    }
  };

  const cancelGeneration = () => {
    cancelRequestedRef.current = true;
    activeRequestRef.current?.abort();
  };

  const ensureFileUploaded = async () => {
    if (fileId) {
      return fileId;
    }

    if (!file) {
      throw new Error('Выберите DOCX-файл');
    }

    const result = await trackRequest(uploadInstructionFile({file}));
    setFileId(result.file_id);

    return result.file_id;
  };

  const convert = async () => {
    if (!hasInstructionSource) {
      setError(inputMode === 'file' ? 'Выберите DOCX-файл' : 'Вставьте текст инструкции');
      return;
    }

    if (!generationOptions.instruction && !generationOptions.aiDescription) {
      setError('Выберите, что нужно сгенерировать');
      return;
    }

    setError(null);
    setCopiedBlock(null);
    cancelRequestedRef.current = false;

    if (generationOptions.instruction) {
      setInstruction(null);
    }

    if (generationOptions.aiDescription) {
      setAiDescription('');
    }

    try {
      const uploadedFileId = inputMode === 'file' ? await ensureFileUploaded() : null;

      if (generationOptions.instruction) {
        if (!uploadedFileId) {
          setError('Генерация HTML-инструкции доступна только для DOCX-файла');
          return;
        }
        const result = await trackRequest(generateInstruction({fileId: uploadedFileId}));
        setInstruction(result);
      }

      if (generationOptions.aiDescription) {
        const result = await trackRequest(generateAiDescription({
          fileId: uploadedFileId ?? undefined,
          instructionText: inputMode === 'text' ? instructionText : undefined,
          productType: generationOptions.aiDescriptionProductType,
          nonMedicineCategory: generationOptions.aiDescriptionProductType === 'non_medicine'
            ? generationOptions.nonMedicineCategory
            : undefined,
        }));
        setAiDescription(result.description);
      }
    } catch (err) {
      setError(cancelRequestedRef.current ? 'Генерация остановлена' : getGenerationErrorMessage(err, 'Не удалось выполнить генерацию'));
    }
  };

  const generateDescriptionOnly = async () => {
    if (!hasInstructionSource) {
      setError(inputMode === 'file' ? 'Выберите DOCX-файл' : 'Вставьте текст инструкции');
      return;
    }

    setError(null);
    setCopiedBlock(null);
    setAiDescription('');
    cancelRequestedRef.current = false;

    try {
      const uploadedFileId = inputMode === 'file' ? await ensureFileUploaded() : null;
      const result = await trackRequest(generateAiDescription({
        fileId: uploadedFileId ?? undefined,
        instructionText: inputMode === 'text' ? instructionText : undefined,
        productType: generationOptions.aiDescriptionProductType,
        nonMedicineCategory: generationOptions.aiDescriptionProductType === 'non_medicine'
          ? generationOptions.nonMedicineCategory
          : undefined,
      }));
      setAiDescription(result.description);
    } catch (err) {
      setError(cancelRequestedRef.current ? 'Генерация остановлена' : getGenerationErrorMessage(err, 'Не удалось сформировать ИИ-описание'));
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
    hasInstructionSource,
    inputMode,
    instruction,
    instructionText,
    isAiDescriptionLoading,
    isFileUploading,
    isInstructionLoading,
    isLoading,
    markupBlocks,
    cancelGeneration,
    convert,
    copyText,
    generateDescriptionOnly,
    removeSelectedFile,
    resetInstruction,
    selectInputMode,
    selectFile,
    updateInstructionText,
    updateGenerationOptions,
  };
}
