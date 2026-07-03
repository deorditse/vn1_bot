import {useMemo, useState} from 'react';

import type {GenerateInstructionResponse} from '../api/types';
import {useGenerateInstructionMutation} from '../api/instructionApi';
import {buildInstructionBlocks} from '../lib/buildInstructionBlocks';

export function useInstructionGenerator() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [instruction, setInstruction] = useState<GenerateInstructionResponse | null>(null);
  const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
  const [generateInstruction, {isLoading}] = useGenerateInstructionMutation();

  const markupBlocks = useMemo(() => buildInstructionBlocks(instruction), [instruction]);

  const selectFile = (nextFile: File) => {
    setFile(nextFile);
    setError(null);
    setInstruction(null);
    setCopiedBlock(null);
  };

  const resetInstruction = () => {
    setFile(null);
    setError(null);
    setInstruction(null);
    setCopiedBlock(null);
  };

  const removeSelectedFile = () => {
    setFile(null);
    setError(null);
    setCopiedBlock(null);
  };

  const convert = async () => {
    if (!file) {
      setError('Выберите DOCX-файл');
      return;
    }

    setError(null);
    setInstruction(null);
    setCopiedBlock(null);

    try {
      const result = await generateInstruction({file}).unwrap();
      setInstruction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сформировать инструкцию');
    }
  };

  const copyText = async (key: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedBlock(key);
    window.setTimeout(() => setCopiedBlock(null), 1600);
  };

  return {
    copiedBlock,
    error,
    file,
    instruction,
    isLoading,
    markupBlocks,
    convert,
    copyText,
    removeSelectedFile,
    resetInstruction,
    selectFile,
  };
}
