import {Alert, Button, Flex, Progress, Typography, Upload} from 'antd';
import type {UploadProps} from 'antd';
import {Download, FileText, UploadCloud} from 'lucide-react';
import {useMemo, useState} from 'react';

import {useGenerateInstructionMutation} from '../api/instructionApi';
import styles from './InstructionPage.module.less';

const {Text, Title} = Typography;

const InstructionPage = () => {
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isDone, setIsDone] = useState(false);
    const [generateInstruction, {isLoading}] = useGenerateInstructionMutation();

    const uploadProps = useMemo<UploadProps>(
        () => ({
            accept: '.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            beforeUpload: (nextFile) => {
                setFile(nextFile);
                setError(null);
                setIsDone(false);
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
                setIsDone(false);
            },
        }),
        [file],
    );

    const convert = async () => {
        if (!file) {
            setError('Выберите DOCX-файл');
            return;
        }

        setError(null);
        setIsDone(false);

        try {
            const blob = await generateInstruction({file}).unwrap();
            downloadBlob(blob, 'instruction.txt');
            setIsDone(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Не удалось сформировать инструкцию');
        }
    };

    return (
        <Flex className={styles.page} vertical>
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

                <Upload.Dragger className={styles.dropzone} disabled={isLoading} {...uploadProps}>
                    <Flex align="center" className={styles.dropContent} gap={10} justify="center" vertical>
                        <UploadCloud size={34}/>
                        <strong>Перетащите DOCX сюда или выберите файл</strong>
                        <span>После обработки будет скачан TXT с блоками MENU и Content.</span>
                    </Flex>
                </Upload.Dragger>

                {isLoading && <Progress percent={70} showInfo={false} status="active"/>}
                {isDone && <Alert message="Файл instruction.txt сформирован и скачан" showIcon type="success"/>}
                {error && <Alert message={error} showIcon type="error"/>}

                <Flex className={styles.actions} justify="flex-end">
                    <Button
                        disabled={!file}
                        icon={<Download size={18}/>}
                        loading={isLoading}
                        onClick={convert}
                        size="large"
                        type="primary"
                    >
                        Сформировать TXT
                    </Button>
                </Flex>
            </Flex>
        </Flex>
    );
}

function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}


export default InstructionPage;
