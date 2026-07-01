import {Button, Flex, Input, Typography} from 'antd';
import {Copy} from 'lucide-react';

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
    <Flex className={styles.block} gap={12} vertical>
      <Flex align="center" gap={12} justify="space-between">
        <Flex gap={8} vertical>
          <Text className={styles.blockTitle}>{block.title}</Text>
          <Text className={styles.blockMeta}>{block.content.length} символов</Text>
        </Flex>
        <Button icon={<Copy size={17} />} onClick={() => onCopy(block.key, block.content)}>
          {copied ? 'Скопировано' : 'Копировать'}
        </Button>
      </Flex>
      <Input.TextArea autoSize={{minRows: 8, maxRows: 18}} className={styles.codeArea} readOnly value={block.content} />
    </Flex>
  );
}
