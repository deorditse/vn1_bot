import {Button, Flex, Typography} from 'antd';
import {Copy, Sparkles} from 'lucide-react';

import {MarkdownPreview} from '@shared/ui/MarkdownPreview';
import type {CopyTextHandler} from '../types';
import styles from './InstructionAiSummary.module.less';

const {Title} = Typography;

type InstructionAiSummaryProps = {
  copied: boolean;
  description: string;
  onCopy: CopyTextHandler;
};

export function InstructionAiSummary({copied, description, onCopy}: InstructionAiSummaryProps) {
  const markdown = description || 'ИИ-описание не вернулось в ответе';

  return (
    <Flex className={styles.summary} gap={14} vertical>
      <Flex align="center" gap={10}>
        <Sparkles size={20} />
        <Title className={styles.sectionTitle} level={3}>
          ИИ-описание
        </Title>
      </Flex>
      <Flex className={styles.summaryPreview} gap={14} vertical>
        <MarkdownPreview markdown={markdown} />
        <Flex justify="flex-end">
          <Button disabled={!description} icon={<Copy size={17} />} onClick={() => onCopy('ai_description', description)}>
            {copied ? 'Скопировано' : 'Копировать описание'}
          </Button>
        </Flex>
      </Flex>
    </Flex>
  );
}
