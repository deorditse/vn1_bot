import {useState} from 'react';

import {DynamicModuleLoader} from '@shared/lib/components/DynamicModuleLoader';
import {Page} from '@widgets/Page';
import {instructionApi, useGenerateInstructionMutation} from '../api/instructionApi';
import type {GenerateInstructionResponse} from '../api/types';
import {InstructionMarkupResults} from './results/InstructionMarkupResults';
import {InstructionAiSummary} from './summary/InstructionAiSummary';
import {InstructionWorkspace} from './workspace/InstructionWorkspace';
import type {InstructionBlock} from './types';

const reducers = {[instructionApi.reducerPath]: instructionApi.reducer};

const InstructionPage = () => {
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [instruction, setInstruction] = useState<GenerateInstructionResponse | null>(null);
    const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
    const [generateInstruction, {isLoading}] = useGenerateInstructionMutation();

    const markupBlocks: InstructionBlock[] = instruction
        ? [
            {
                key: 'html_menu',
                title: 'HTML-меню',
                content: instruction.html_menu,
            },
            {
                key: 'html_content',
                title: 'HTML-контент',
                content: instruction.html_content,
            },
        ]
        : [];

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

    return (
        <DynamicModuleLoader reducers={reducers}>
            <Page>
                <InstructionWorkspace
                    error={error}
                    file={file}
                    instructionReady={Boolean(instruction)}
                    isLoading={isLoading}
                    onConvert={convert}
                    onRemoveFile={removeSelectedFile}
                    onReset={resetInstruction}
                    onSelectFile={selectFile}
                />

                {instruction && (
                    <>
                        <InstructionMarkupResults blocks={markupBlocks} copiedBlock={copiedBlock} onCopy={copyText}/>
                        <InstructionAiSummary
                            copied={copiedBlock === 'ai_description'}
                            description={instruction.ai_description}
                            onCopy={copyText}
                        />
                    </>
                )}
            </Page>
        </DynamicModuleLoader>
    );
};

export default InstructionPage;
