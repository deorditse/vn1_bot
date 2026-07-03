import {Typography} from 'antd';

import {Card, VStack} from '@shared/ui';
import type {CopyTextHandler, InstructionBlock} from '../../../model/types';
import {InstructionBlockView} from '../InstructionBlockView';
import styles from './InstructionMarkupResults.module.less';

const {Title} = Typography;

type InstructionMarkupResultsProps = {
  blocks: InstructionBlock[];
  copiedBlock: string | null;
  onCopy: CopyTextHandler;
};

export function InstructionMarkupResults({blocks, copiedBlock, onCopy}: InstructionMarkupResultsProps) {
  return (
    <Card className={styles.results} padding="22">
      <VStack gap="16" max>
      <Title className={styles.sectionTitle} level={3}>
        Разметка инструкции
      </Title>
      {blocks.map((block) => (
        <InstructionBlockView block={block} copied={copiedBlock === block.key} key={block.key} onCopy={onCopy} />
      ))}
      </VStack>
    </Card>
  );
}

export default InstructionMarkupResults;
