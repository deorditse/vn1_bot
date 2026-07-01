import {Button, Flex, Typography} from 'antd';
import {FileText, RefreshCcw} from 'lucide-react';

import styles from './InstructionLoadedState.module.less';

const {Text} = Typography;

type InstructionLoadedStateProps = {
  fileName?: string;
  onReset: () => void;
};

export function InstructionLoadedState({fileName, onReset}: InstructionLoadedStateProps) {
  return (
    <Flex align="center" className={styles.loadedState} gap={14} justify="space-between" wrap="wrap">
      <Flex align="center" gap={12}>
        <Flex align="center" className={styles.loadedIcon} justify="center">
          <FileText size={20} />
        </Flex>
        <Flex vertical>
          <Text className={styles.loadedLabel}>Загружена 1 инструкция</Text>
          <Text className={styles.loadedFile}>{fileName ?? 'DOCX-файл обработан'}</Text>
        </Flex>
      </Flex>
      <Button icon={<RefreshCcw size={17} />} onClick={onReset}>
        Новая инструкция
      </Button>
    </Flex>
  );
}
