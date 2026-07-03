import {Button, Typography} from 'antd';
import {FileText, RefreshCcw} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import styles from './InstructionLoadedState.module.less';

const {Text} = Typography;

type InstructionLoadedStateProps = {
  fileName?: string;
  onReset: () => void;
};

export function InstructionLoadedState({fileName, onReset}: InstructionLoadedStateProps) {
  return (
    <Card className={styles.loadedState} padding="18" variant="light">
      <HStack align="center" gap="14" justify="between" max wrap="wrap">
      <HStack align="center" gap="12">
        <HStack align="center" className={styles.loadedIcon} justify="center">
          <FileText size={20} />
        </HStack>
        <VStack>
          <Text className={styles.loadedLabel}>Загружена 1 инструкция</Text>
          <Text className={styles.loadedFile}>{fileName ?? 'DOCX-файл обработан'}</Text>
        </VStack>
      </HStack>
      <Button icon={<RefreshCcw size={17} />} onClick={onReset}>
        Новая инструкция
      </Button>
      </HStack>
    </Card>
  );
}
