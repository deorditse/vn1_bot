import {Card, Skeleton, VStack} from '@shared/ui';

export function InstructionResultsSkeleton() {
  return (
    <Card padding="22">
      <VStack gap="16" max>
        <Skeleton border="12px" height={28} width="240px" />
        <Skeleton border="16px" height={280} width="100%" />
      </VStack>
    </Card>
  );
}

export function InstructionMarkupResultsSkeleton() {
  return (
    <Card padding="22">
      <VStack gap="16" max>
        <Skeleton border="12px" height={28} width="210px" />
        <Skeleton border="14px" height={120} width="100%" />
        <Skeleton border="14px" height={220} width="100%" />
      </VStack>
    </Card>
  );
}
