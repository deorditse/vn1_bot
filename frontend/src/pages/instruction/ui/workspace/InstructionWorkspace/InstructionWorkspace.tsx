import {Alert, Button, Progress, Typography} from 'antd';
import {FileText} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import {InstructionLoadedState} from '../InstructionLoadedState';
import {InstructionUploadPanel} from '../InstructionUploadPanel';
import styles from './InstructionWorkspace.module.less';

const {Text} = Typography;

type InstructionWorkspaceProps = {
  error: string | null;
  file: File | null;
  instructionReady: boolean;
  isLoading: boolean;
  onConvert: () => void;
  onRemoveFile: () => void;
  onReset: () => void;
  onSelectFile: (file: File) => void;
};

export function InstructionWorkspace({
  error,
  file,
  instructionReady,
  isLoading,
  onConvert,
  onRemoveFile,
  onReset,
  onSelectFile,
}: InstructionWorkspaceProps) {
  return (
    <Card className={styles.workspace} padding="24">
      <VStack gap="22" max>
      <HStack align="center" gap="14">
        <HStack align="center" className={styles.iconBox} justify="center">
          <FileText size={22} />
        </HStack>
        <Text className={styles.kicker}>Генератор</Text>
      </HStack>

      {!instructionReady ? (
        <InstructionUploadPanel
          file={file}
          instructionReady={instructionReady}
          isLoading={isLoading}
          onRemoveFile={onRemoveFile}
          onSelectFile={onSelectFile}
        />
      ) : (
        <InstructionLoadedState fileName={file?.name} onReset={onReset} />
      )}

      {isLoading && <Progress percent={70} showInfo={false} status="active" />}
      {instructionReady && <Alert message="Инструкция сформирована" showIcon type="success" />}
      {error && <Alert message={error} showIcon type="error" />}

      <HStack className={styles.actions} gap="12" justify="end" max wrap="wrap">
        <Button
          disabled={!file || instructionReady}
          icon={<FileText size={18} />}
          loading={isLoading}
          onClick={onConvert}
          size="large"
          type="primary"
        >
          Сформировать инструкцию
        </Button>
      </HStack>
      </VStack>
    </Card>
  );
}
