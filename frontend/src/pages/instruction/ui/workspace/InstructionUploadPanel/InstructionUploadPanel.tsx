import {Button, Input, Segmented, Upload} from 'antd';
import type {UploadProps} from 'antd';
import {FileCheck2, FileText, TextCursorInput, Trash2, UploadCloud} from 'lucide-react';
import {useMemo} from 'react';
import type {MouseEvent} from 'react';

import {HStack, VStack} from '@shared/ui';
import type {InstructionInputMode} from '../../../model/types';
import styles from './InstructionUploadPanel.module.less';

const {TextArea} = Input;

type InstructionUploadPanelProps = {
  file: File | null;
  inputMode: InstructionInputMode;
  instructionText: string;
  instructionReady: boolean;
  isLoading: boolean;
  onRemoveFile: () => void;
  onSelectInputMode: (mode: InstructionInputMode) => void;
  onSelectFile: (file: File) => void;
  onTextChange: (value: string) => void;
};

function formatFileSize(size: number) {
  if (size < 1024) {
    return `${size} Б`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} КБ`;
  }

  return `${(size / 1024 / 1024).toFixed(1)} МБ`;
}

export function InstructionUploadPanel({
  file,
  inputMode,
  instructionText,
  instructionReady,
  isLoading,
  onRemoveFile,
  onSelectInputMode,
  onSelectFile,
  onTextChange,
}: InstructionUploadPanelProps) {
  const handleRemoveFile = (event: MouseEvent<HTMLElement>) => {
    event.preventDefault();
    event.stopPropagation();
    onRemoveFile();
  };

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
      <Segmented
        className={styles.sourceSwitch}
        disabled={isLoading || instructionReady}
        onChange={(value) => onSelectInputMode(value as InstructionInputMode)}
        options={[
          {icon: <FileText size={16} />, label: 'DOCX', value: 'file'},
          {icon: <TextCursorInput size={16} />, label: 'Текст', value: 'text'},
        ]}
        value={inputMode}
      />

      {inputMode === 'file' ? (
        <Upload.Dragger className={styles.dropzone} disabled={isLoading} {...uploadProps}>
          {file ? (
            <HStack align="center" className={styles.selectedContent} gap="14" justify="between" max>
              <HStack align="center" className={styles.selectedFileSummary} gap="12">
                <HStack align="center" className={styles.selectedFileIcon} justify="center">
                  <FileCheck2 size={22} />
                </HStack>
                <VStack className={styles.selectedFileInfo} gap="4">
                  <strong className={styles.selectedFileName}>{file.name}</strong>
                  <span className={styles.selectedFileMeta}>Выбран DOCX-файл, {formatFileSize(file.size)}</span>
                </VStack>
              </HStack>

              <HStack className={styles.selectedFileActions} gap="8">
                <Button disabled={isLoading} icon={<Trash2 size={16} />} onClick={handleRemoveFile}>
                  Удалить
                </Button>
                <Button disabled={isLoading} icon={<UploadCloud size={16} />} type="primary">
                  Загрузить новый
                </Button>
              </HStack>
            </HStack>
          ) : (
            <HStack align="center" className={styles.dropContent} gap="14" justify="center">
              <HStack align="center" className={styles.uploadIcon} justify="center">
                <UploadCloud size={24} />
              </HStack>
              <VStack className={styles.uploadText} gap="4">
                <strong>Загрузите инструкцию в DOCX</strong>
                <span>Перетащите файл сюда или нажмите для выбора. Максимум один файл.</span>
              </VStack>
            </HStack>
          )}
        </Upload.Dragger>
      ) : (
        <VStack className={styles.textInputPanel} gap="8" max>
          <TextArea
            autoSize={{minRows: 8, maxRows: 18}}
            className={styles.instructionTextArea}
            disabled={isLoading || instructionReady}
            onChange={(event) => onTextChange(event.target.value)}
            placeholder="Вставьте полный текст инструкции или сведения о товаре"
            value={instructionText}
          />
          <HStack justify="between" max>
            <span className={styles.textInputMeta}>Для текста доступно только краткое описание</span>
            <span className={styles.textInputCounter}>{instructionText.trim().length} символов</span>
          </HStack>
        </VStack>
      )}
    </VStack>
  );
}
