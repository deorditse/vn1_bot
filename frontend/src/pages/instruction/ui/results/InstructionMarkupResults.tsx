import {Flex, Typography} from 'antd';

import type {CopyTextHandler, InstructionBlock} from '../types';
import {InstructionBlockView} from './InstructionBlockView';
import styles from './InstructionMarkupResults.module.less';

const {Title} = Typography;

type InstructionMarkupResultsProps = {
  blocks: InstructionBlock[];
  copiedBlock: string | null;
  onCopy: CopyTextHandler;
};

export function InstructionMarkupResults({blocks, copiedBlock, onCopy}: InstructionMarkupResultsProps) {
  return (
    <Flex className={styles.results} gap={16} vertical>
      <Title className={styles.sectionTitle} level={3}>
        Разметка инструкции
      </Title>
      {blocks.map((block) => (
        <InstructionBlockView block={block} copied={copiedBlock === block.key} key={block.key} onCopy={onCopy} />
      ))}
    </Flex>
  );
}
