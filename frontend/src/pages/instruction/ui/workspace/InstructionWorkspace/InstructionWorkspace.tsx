import {Alert, Button, Progress, Typography} from 'antd';
import {FileText, Sparkles} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import type {GenerationOptions, InstructionInputMode} from '../../../model/types';
import {InstructionLoadedState} from '../InstructionLoadedState';
import {InstructionUploadPanel} from '../InstructionUploadPanel';
import {GenerationOptionsPicker} from './ui/GenerationOptionsPicker/GenerationOptionsPicker';
import styles from './InstructionWorkspace.module.less';

const {Text} = Typography;

type InstructionWorkspaceProps = {
    error: string | null;
    file: File | null;
    generationOptions: GenerationOptions;
    hasInstructionSource: boolean;
    inputMode: InstructionInputMode;
    instructionText: string;
    instructionReady: boolean;
    isLoading: boolean;
    onConvert: () => void;
    onOptionsChange: (options: GenerationOptions) => void;
    onRemoveFile: () => void;
    onReset: () => void;
    onSelectInputMode: (mode: InstructionInputMode) => void;
    onSelectFile: (file: File) => void;
    onTextChange: (value: string) => void;
};

export function InstructionWorkspace({
                                         error,
                                         file,
                                         generationOptions,
                                         hasInstructionSource,
                                         inputMode,
                                         instructionText,
                                         instructionReady,
                                         isLoading,
                                         onConvert,
                                         onOptionsChange,
                                         onRemoveFile,
                                         onReset,
                                         onSelectInputMode,
                                         onSelectFile,
                                         onTextChange,
                                     }: InstructionWorkspaceProps) {
    return (
        <Card className={styles.workspace} padding="24">
            <VStack gap="22" max>
                <HStack align="center" gap="14">
                    <HStack align="center" className={styles.iconBox} justify="center">
                        <FileText size={22}/>
                    </HStack>
                    <div className={styles.sectionHeading}>
                        <Text strong>1. Добавьте исходную инструкцию</Text>
                        <Text>Загрузите DOCX или вставьте текст, если нужно только краткое описание.</Text>
                    </div>
                </HStack>

                {!instructionReady ? (
                    <InstructionUploadPanel
                        file={file}
                        inputMode={inputMode}
                        instructionText={instructionText}
                        instructionReady={instructionReady}
                        isLoading={isLoading}
                        onRemoveFile={onRemoveFile}
                        onSelectInputMode={onSelectInputMode}
                        onSelectFile={onSelectFile}
                        onTextChange={onTextChange}
                    />
                ) : (
                    <InstructionLoadedState
                        fileName={inputMode === 'file' ? file?.name : 'Текст инструкции'}
                        sourceText={inputMode === 'text' ? instructionText : undefined}
                        onReset={onReset}
                    />
                )}

                <div className={styles.sectionHeading}>
                    <Text strong>2. Выберите результат</Text>
                    <Text>Можно создать HTML-инструкцию, краткое описание или оба варианта сразу.</Text>
                </div>

                <GenerationOptionsPicker
                    disabled={isLoading}
                    instructionDisabled={inputMode === 'text'}
                    generationOptions={generationOptions}
                    onOptionsChange={onOptionsChange}
                />

                <VStack gap="8" max>
                    {isLoading && <Progress percent={70} showInfo={false} status="active"/>}
                    {instructionReady && <Alert message="Генерация выполнена" showIcon type="success"/>}
                    {error && <Alert message={error} showIcon type="error"/>}
                </VStack>

                <HStack className={styles.actions} justify="end" max wrap="wrap">
                    <Button
                        disabled={!hasInstructionSource || isLoading || (!generationOptions.instruction && !generationOptions.aiDescription)}
                        icon={generationOptions.aiDescription && !generationOptions.instruction ?
                            <Sparkles size={18}/> : <FileText size={18}/>}
                        loading={isLoading}
                        onClick={onConvert}
                        size="large"
                        type="primary"
                    >
                        {generationOptions.instruction && generationOptions.aiDescription
                            ? 'Создать инструкцию и описание'
                            : generationOptions.instruction
                                ? 'Создать HTML-инструкцию'
                                : 'Создать краткое описание'}
                    </Button>
                </HStack>
            </VStack>
        </Card>
    );
}
