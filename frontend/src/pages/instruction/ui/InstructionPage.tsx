import {Alert, Button, Flex, Input, Progress, Typography, Upload} from 'antd';
import type {UploadProps} from 'antd';
import {Copy, FileCheck2, FileText, RefreshCcw, Sparkles, Trash2, UploadCloud} from 'lucide-react';
import {useMemo, useState} from 'react';

import {DynamicModuleLoader} from '@shared/lib/components/DynamicModuleLoader';
import {instructionApi, useGenerateInstructionMutation} from '../api/instructionApi';
import type {GenerateInstructionResponse} from '../api/types';
import styles from './InstructionPage.module.less';

const {Paragraph, Text, Title} = Typography;
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
                title: 'HTML menu',
                content: instruction.html_menu,
            },
            {
                key: 'html_content',
                title: 'HTML content',
                content: instruction.html_content,
            },
        ]
        : [];

    const uploadProps = useMemo<UploadProps>(
        () => ({
            accept: '.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            beforeUpload: (nextFile) => {
                if (isLoading || instruction) {
                    return Upload.LIST_IGNORE;
                }

                setFile(nextFile);
                setError(null);
                setInstruction(null);
                setCopiedBlock(null);
                return false;
            },
            fileList: file
                ? [
                    {
                        uid: file.name,
                        name: file.name,
                        status: 'done',
                    },
                ]
                : [],
            maxCount: 1,
            onRemove: () => {
                setFile(null);
                setInstruction(null);
                setCopiedBlock(null);
            },
            showUploadList: false,
        }),
        [file, instruction, isLoading],
    );

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
        <Flex className={styles.page} gap={18} vertical>
            <Flex className={styles.workspace} gap={22} vertical>
                <Flex align="center" gap={14}>
                    <Flex align="center" className={styles.iconBox} justify="center">
                        <FileText size={22}/>
                    </Flex>
                    <Flex vertical>
                        <Text className={styles.kicker}>Generator</Text>
                        <Title className={styles.title} level={2}>
                            DOCX в instruction.txt
                        </Title>
                    </Flex>
                </Flex>

                {!instruction ? (
                    <Flex gap={12} vertical>
                        <Upload.Dragger className={styles.dropzone} disabled={isLoading} {...uploadProps}>
                            <Flex align="center" className={styles.dropContent} gap={14} justify="center">
                                <Flex align="center" className={styles.uploadIcon} justify="center">
                                    <UploadCloud size={24}/>
                                </Flex>
                                <Flex className={styles.uploadText} vertical>
                                    <strong>{file ? 'Файл выбран' : 'Добавьте DOCX-инструкцию'}</strong>
                                    <span>{file ? 'Для замены удалите текущий файл.' : 'Перетащите файл сюда или выберите вручную.'}</span>
                                </Flex>
                            </Flex>
                        </Upload.Dragger>

                        {file && (
                            <Flex align="center" className={styles.selectedFileBar} gap={12} justify="space-between">
                                <Flex align="center" gap={10}>
                                    <Flex align="center" className={styles.selectedFileIcon} justify="center">
                                        <FileCheck2 size={18}/>
                                    </Flex>
                                    <Flex className={styles.selectedFileInfo} vertical>
                                        <Text className={styles.selectedFileLabel}>Готов к обработке</Text>
                                        <Text className={styles.selectedFileName}>{file.name}</Text>
                                    </Flex>
                                </Flex>
                                <Button disabled={isLoading} icon={<Trash2 size={17}/>} onClick={removeSelectedFile} type="text"/>
                            </Flex>
                        )}
                    </Flex>
                ) : (
                    <Flex align="center" className={styles.loadedState} gap={14} justify="space-between" wrap="wrap">
                        <Flex align="center" gap={12}>
                            <Flex align="center" className={styles.loadedIcon} justify="center">
                                <FileText size={20}/>
                            </Flex>
                            <Flex vertical>
                                <Text className={styles.loadedLabel}>Загружена 1 инструкция</Text>
                                <Text className={styles.loadedFile}>{file?.name ?? 'DOCX-файл обработан'}</Text>
                            </Flex>
                        </Flex>
                        <Button icon={<RefreshCcw size={17}/>} onClick={resetInstruction}>
                            Новая инструкция
                        </Button>
                    </Flex>
                )}

                {isLoading && <Progress percent={70} showInfo={false} status="active"/>}
                {instruction && <Alert message="Инструкция сформирована" showIcon type="success"/>}
                {error && <Alert message={error} showIcon type="error"/>}

                <Flex className={styles.actions} gap={12} justify="flex-end" wrap="wrap">
                    <Button
                        disabled={!file || Boolean(instruction)}
                        icon={<FileText size={18}/>}
                        loading={isLoading}
                        onClick={convert}
                        size="large"
                        type="primary"
                    >
                        Сформировать инструкцию
                    </Button>
                </Flex>
            </Flex>

            {instruction && (
                <Flex className={styles.results} gap={16} vertical>
                    <Title className={styles.sectionTitle} level={3}>Разметка инструкции</Title>
                    {markupBlocks.map((block) => (
                        <InstructionBlockView
                            block={block}
                            copied={copiedBlock === block.key}
                            key={block.key}
                            onCopy={copyText}
                        />
                    ))}
                </Flex>
            )}

            {instruction && (
                <Flex className={styles.summary} gap={14} vertical>
                    <Flex align="center" gap={10}>
                        <Sparkles size={20}/>
                        <Title className={styles.sectionTitle} level={3}>ИИ обзор</Title>
                    </Flex>
                    <Flex className={styles.summaryPreview} gap={14} vertical>
                        <Paragraph className={styles.summaryText}>
                            {instruction.ai_description || 'ИИ-описание не вернулось в ответе'}
                        </Paragraph>
                        <Flex justify="flex-end">
                            <Button
                                disabled={!instruction.ai_description}
                                icon={<Copy size={17}/>}
                                onClick={() => copyText('ai_description', instruction.ai_description)}
                            >
                                {copiedBlock === 'ai_description' ? 'Скопировано' : 'Копировать обзор'}
                            </Button>
                        </Flex>
                    </Flex>
                </Flex>
            )}
        </Flex>
        </DynamicModuleLoader>
    );
};

type InstructionBlockViewProps = {
    block: InstructionBlock;
    copied: boolean;
    onCopy: (key: string, content: string) => Promise<void>;
};

type InstructionBlock = {
    key: string;
    title: string;
    content: string;
};

function InstructionBlockView({block, copied, onCopy}: InstructionBlockViewProps) {
    return (
        <Flex className={styles.block} gap={12} vertical>
            <Flex align="center" gap={12} justify="space-between">
                <Flex gap={8} vertical>
                    <Text className={styles.blockTitle}>{block.title}</Text>
                    <Text className={styles.blockMeta}>{block.content.length} символов</Text>
                </Flex>
                <Button icon={<Copy size={17}/>} onClick={() => onCopy(block.key, block.content)}>
                    {copied ? 'Скопировано' : 'Копировать'}
                </Button>
            </Flex>
            <Input.TextArea
                autoSize={{minRows: 8, maxRows: 18}}
                className={styles.codeArea}
                readOnly
                value={block.content}
            />
        </Flex>
    );
}


export default InstructionPage;
