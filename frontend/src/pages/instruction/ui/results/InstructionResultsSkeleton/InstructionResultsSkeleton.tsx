import {Typography} from 'antd';

import {Card, Skeleton, VStack} from '@shared/ui';
import styles from './InstructionResultsSkeleton.module.less';

const {Title} = Typography;

export function InstructionResultsSkeleton({title = 'Разметка инструкции'}: {title?: string}) {
  return (
    <Card padding="22">
      <VStack gap="16" max>
        <Title className={styles.title} level={3}>{title}</Title>
        <Skeleton border="16px" height={280} width="100%" />
      </VStack>
    </Card>
  );
}

export function InstructionMarkupResultsSkeleton() {
  return (
    <Card padding="22">
      <VStack gap="16" max>
        <Title className={styles.title} level={3}>Разметка инструкции</Title>
        <Skeleton border="14px" height={120} width="100%" />
        <Skeleton border="14px" height={220} width="100%" />
      </VStack>
    </Card>
  );
}
