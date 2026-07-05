import {Card, HStack, Skeleton, VStack} from '@shared/ui';

import styles from './InstructionAiSummary.module.less';

export function InstructionAiSummarySkeleton() {
  return (
    <Card className={styles.summary} padding="22">
      <VStack gap="14" max>
        <HStack align="center" gap="10">
          <Skeleton border="10px" height={20} width={20} />
          <Skeleton border="12px" height={24} width="150px" />
        </HStack>
        <Card className={styles.summaryPreview} padding="16" variant="light">
          <VStack gap="12" max>
            <Skeleton border="12px" height={18} width="92%" />
            <Skeleton border="12px" height={18} width="86%" />
            <Skeleton border="12px" height={18} width="74%" />
            <HStack justify="end" max>
              <Skeleton border="8px" height={32} width="180px" />
            </HStack>
          </VStack>
        </Card>
      </VStack>
    </Card>
  );
}
