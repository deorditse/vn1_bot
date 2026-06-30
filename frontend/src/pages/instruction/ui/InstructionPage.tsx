import { Alert, Button, Progress, Typography, Upload } from 'antd';
import type { UploadProps } from 'antd';
import { Download, FileText, UploadCloud } from 'lucide-react';
import { useMemo, useState } from 'react';

import { downloadInstruction } from '@features/instruction/api/instructionApi';
import styles from './InstructionPage.module.less';

const { Text, Title } = Typography;

export function InstructionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDone, setIsDone] = useState(false);

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
    setIsLoading(true);

    try {
      await downloadInstruction(file);
      setIsDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сформировать инструкцию');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <section className={styles.workspace}>
        <div className={styles.intro}>
          <span>
            <FileText size={22} />
          </span>
          <div>
            <Text className={styles.kicker}>Generator</Text>
            <Title level={2}>DOCX в instruction.txt</Title>
          </div>
        </div>

        <Upload.Dragger className={styles.dropzone} disabled={isLoading} {...uploadProps}>
          <div className={styles.dropContent}>
            <UploadCloud size={34} />
            <strong>Перетащите DOCX сюда или выберите файл</strong>
            <span>После обработки будет скачан TXT с блоками MENU и Content.</span>
          </div>
        </Upload.Dragger>

        {isLoading && <Progress percent={70} showInfo={false} status="active" />}
        {isDone && <Alert message="Файл instruction.txt сформирован и скачан" showIcon type="success" />}
        {error && <Alert message={error} showIcon type="error" />}

        <div className={styles.actions}>
          <Button
            disabled={!file}
            icon={<Download size={18} />}
            loading={isLoading}
            onClick={convert}
            size="large"
            type="primary"
          >
            Сформировать TXT
          </Button>
        </div>
      </section>
    </div>
  );
}
