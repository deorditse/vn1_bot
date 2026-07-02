import {Upload} from 'antd';
import type {UploadProps} from 'antd';
import {UploadCloud} from 'lucide-react';
import {useMemo} from 'react';

import {HStack, VStack} from '@shared/ui';
import styles from './InstructionUploadPanel.module.less';
import {SelectedFileBar} from './SelectedFileBar';

type InstructionUploadPanelProps = {
  file: File | null;
  instructionReady: boolean;
  isLoading: boolean;
  onRemoveFile: () => void;
  onSelectFile: (file: File) => void;
};

export function InstructionUploadPanel({
  file,
  instructionReady,
  isLoading,
  onRemoveFile,
  onSelectFile,
}: InstructionUploadPanelProps) {
  const uploadProps = useMemo<UploadProps>(
    () => ({
      accept: '.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      beforeUpload: (nextFile) => {
        if (isLoading || instructionReady) {
          return Upload.LIST_IGNORE;
        }

        onSelectFile(nextFile);
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
        onRemoveFile();
      },
      showUploadList: false,
    }),
    [file, instructionReady, isLoading, onRemoveFile, onSelectFile],
  );

  return (
    <VStack gap="12" max>
      <Upload.Dragger className={styles.dropzone} disabled={isLoading} {...uploadProps}>
        <HStack align="center" className={styles.dropContent} gap="14" justify="center">
          <HStack align="center" className={styles.uploadIcon} justify="center">
            <UploadCloud size={24} />
          </HStack>
          <VStack className={styles.uploadText} gap="4">
            <strong>{file ? 'Файл выбран' : 'Добавьте DOCX-инструкцию'}</strong>
            <span>{file ? 'Для замены удалите текущий файл.' : 'Перетащите файл сюда или выберите вручную.'}</span>
          </VStack>
        </HStack>
      </Upload.Dragger>

      {file && (
        <SelectedFileBar disabled={isLoading} fileName={file.name} label="Готов к обработке" onRemove={onRemoveFile} />
      )}
    </VStack>
  );
}
