import {Button, Typography} from 'antd';
import {Copy, Sparkles} from 'lucide-react';

import {Card, HStack, MarkdownPreview, VStack} from '@shared/ui';
import type {CopyTextHandler} from '../../../model/types';
import styles from './InstructionAiSummary.module.less';

const {Title} = Typography;

type InstructionAiSummaryProps = {
  copied: boolean;
  description: string;
  isLoading: boolean;
  onCopy: CopyTextHandler;
  onGenerate: () => void;
};

export function InstructionAiSummary({copied, description, isLoading, onCopy, onGenerate}: InstructionAiSummaryProps) {
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
        {description ? (
          <MarkdownPreview markdown={description} />
        ) : (
          <Typography.Text className={styles.emptyDescription}>ИИ-описание еще не сформировано</Typography.Text>
        )}
        <HStack justify="end" max>
          {description ? (
            <Button disabled={!description} icon={<Copy size={17} />} onClick={() => onCopy('ai_description', description)}>
              {copied ? 'Скопировано' : 'Копировать описание'}
            </Button>
          ) : (
            <Button icon={<Sparkles size={17} />} loading={isLoading} onClick={onGenerate} type="primary">
              Сгенерировать ИИ-описание
            </Button>
          )}
        </HStack>
        </VStack>
      </Card>
      </VStack>
    </Card>
  );
}

export default InstructionAiSummary;
