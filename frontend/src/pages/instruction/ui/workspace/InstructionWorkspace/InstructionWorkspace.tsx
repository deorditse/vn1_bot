import {Alert, Button, Checkbox, Progress, Typography} from 'antd';
import {FileText, Sparkles} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import type {GenerationOptions} from '../../../model/types';
import {InstructionLoadedState} from '../InstructionLoadedState';
import {InstructionUploadPanel} from '../InstructionUploadPanel';
import styles from './InstructionWorkspace.module.less';

const {Text} = Typography;

type InstructionWorkspaceProps = {
  error: string | null;
  file: File | null;
  generationOptions: GenerationOptions;
  instructionReady: boolean;
  isLoading: boolean;
  onConvert: () => void;
  onOptionsChange: (options: GenerationOptions) => void;
  onRemoveFile: () => void;
  onReset: () => void;
  onSelectFile: (file: File) => void;
};

export function InstructionWorkspace({
  error,
  file,
  generationOptions,
  instructionReady,
  isLoading,
  onConvert,
  onOptionsChange,
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

      <HStack className={styles.options} gap="16" max wrap="wrap">
        <Checkbox
          checked={generationOptions.instruction}
          disabled={isLoading}
          onChange={(event) => onOptionsChange({...generationOptions, instruction: event.target.checked})}
        >
          Генерация инструкции
        </Checkbox>
        <Checkbox
          checked={generationOptions.aiDescription}
          disabled={isLoading}
          onChange={(event) => onOptionsChange({...generationOptions, aiDescription: event.target.checked})}
        >
          Генерация ИИ-описания
        </Checkbox>
      </HStack>

      {isLoading && <Progress percent={70} showInfo={false} status="active" />}
      {instructionReady && <Alert message="Генерация выполнена" showIcon type="success" />}
      {error && <Alert message={error} showIcon type="error" />}

      <HStack className={styles.actions} gap="12" justify="end" max wrap="wrap">
        <Button
          disabled={!file || isLoading || (!generationOptions.instruction && !generationOptions.aiDescription)}
          icon={generationOptions.aiDescription && !generationOptions.instruction ? <Sparkles size={18} /> : <FileText size={18} />}
          loading={isLoading}
          onClick={onConvert}
          size="large"
          type="primary"
        >
          Сгенерировать
        </Button>
      </HStack>
      </VStack>
    </Card>
  );
}
