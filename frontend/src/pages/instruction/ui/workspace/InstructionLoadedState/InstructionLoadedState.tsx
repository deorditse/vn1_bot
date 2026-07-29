import {Button, Input, Typography} from 'antd';
import {ChevronDown, FileText, RefreshCcw} from 'lucide-react';
import {useState} from 'react';

import {Card, HStack, VStack} from '@shared/ui';
import styles from './InstructionLoadedState.module.less';

const {Text} = Typography;
const {TextArea} = Input;

type InstructionLoadedStateProps = {
  fileName?: string;
  sourceText?: string;
  onReset: () => void;
};

export function InstructionLoadedState({fileName, sourceText, onReset}: InstructionLoadedStateProps) {
  const [isSourceOpen, setIsSourceOpen] = useState(false);
  const hasSourceText = Boolean(sourceText?.trim());

  return (
    <Card className={styles.loadedState} padding="18" variant="light">
      <VStack gap="14" max>
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
          <HStack gap="8" wrap="wrap">
            {hasSourceText ? (
              <Button
                className={isSourceOpen ? styles.sourceButtonOpen : undefined}
                icon={<ChevronDown size={17} />}
                onClick={() => setIsSourceOpen((value) => !value)}
              >
                Исходный текст
              </Button>
            ) : null}
            <Button icon={<RefreshCcw size={17} />} onClick={onReset}>
              Новая инструкция
            </Button>
          </HStack>
        </HStack>

        {hasSourceText && isSourceOpen ? (
          <TextArea
            autoSize={{minRows: 6, maxRows: 14}}
            className={styles.sourceText}
            readOnly
            value={sourceText}
          />
        ) : null}
      </VStack>
    </Card>
  );
}
