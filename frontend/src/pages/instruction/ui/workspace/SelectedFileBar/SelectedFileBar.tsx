import {Button, Typography} from 'antd';
import {FileCheck2, Trash2} from 'lucide-react';

import {Card, HStack, VStack} from '@shared/ui';
import styles from './SelectedFileBar.module.less';

const {Text} = Typography;

type SelectedFileBarProps = {
  disabled?: boolean;
  fileName: string;
  label: string;
  onRemove: () => void;
};

export function SelectedFileBar({disabled, fileName, label, onRemove}: SelectedFileBarProps) {
  return (
    <Card className={styles.selectedFileBar} padding="12" variant="outlined">
      <HStack align="center" gap="12" justify="between" max>
      <HStack align="center" gap="10">
        <HStack align="center" className={styles.selectedFileIcon} justify="center">
          <FileCheck2 size={18} />
        </HStack>
        <VStack className={styles.selectedFileInfo}>
          <Text className={styles.selectedFileLabel}>{label}</Text>
          <Text className={styles.selectedFileName}>{fileName}</Text>
        </VStack>
      </HStack>
      <Button disabled={disabled} icon={<Trash2 size={17} />} onClick={onRemove} type="text" />
      </HStack>
    </Card>
  );
}
