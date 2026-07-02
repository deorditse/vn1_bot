import {Button, Typography} from 'antd';
import {Copy, Sparkles} from 'lucide-react';

import {Card, HStack, MarkdownPreview, VStack} from '@shared/ui';
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
    <Card className={styles.summary} padding="22">
      <VStack gap="14" max>
      <HStack align="center" gap="10">
        <Sparkles size={20} />
        <Title className={styles.sectionTitle} level={3}>
          ИИ-описание
        </Title>
      </HStack>
      <Card className={styles.summaryPreview} padding="16" variant="light">
        <VStack gap="14" max>
        <MarkdownPreview markdown={markdown} />
        <HStack justify="end" max>
          <Button disabled={!description} icon={<Copy size={17} />} onClick={() => onCopy('ai_description', description)}>
            {copied ? 'Скопировано' : 'Копировать описание'}
          </Button>
        </HStack>
        </VStack>
      </Card>
      </VStack>
    </Card>
  );
}
