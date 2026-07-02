import {Button, Input, Typography} from 'antd';
import {Copy} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import type {CopyTextHandler, InstructionBlock} from '../types';
import styles from './InstructionBlockView.module.less';

const {Text} = Typography;

type InstructionBlockViewProps = {
  block: InstructionBlock;
  copied: boolean;
  onCopy: CopyTextHandler;
};

export function InstructionBlockView({block, copied, onCopy}: InstructionBlockViewProps) {
  return (
    <Card className={styles.block} padding="16" variant="outlined">
      <VStack gap="12" max>
      <HStack align="center" gap="12" justify="between" max>
        <VStack gap="8">
          <Text className={styles.blockTitle}>{block.title}</Text>
          <Text className={styles.blockMeta}>{block.content.length} символов</Text>
        </VStack>
        <Button icon={<Copy size={17} />} onClick={() => onCopy(block.key, block.content)}>
          {copied ? 'Скопировано' : 'Копировать'}
        </Button>
      </HStack>
      <Input.TextArea autoSize={{minRows: 8, maxRows: 18}} className={styles.codeArea} readOnly value={block.content} />
      </VStack>
    </Card>
  );
}
