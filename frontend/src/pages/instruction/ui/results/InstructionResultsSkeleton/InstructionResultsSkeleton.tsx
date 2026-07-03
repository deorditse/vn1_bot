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
