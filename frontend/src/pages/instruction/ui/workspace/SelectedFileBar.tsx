import {Button, Flex, Typography} from 'antd';
import {FileCheck2, Trash2} from 'lucide-react';

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
    <Flex align="center" className={styles.selectedFileBar} gap={12} justify="space-between">
      <Flex align="center" gap={10}>
        <Flex align="center" className={styles.selectedFileIcon} justify="center">
          <FileCheck2 size={18} />
        </Flex>
        <Flex className={styles.selectedFileInfo} vertical>
          <Text className={styles.selectedFileLabel}>{label}</Text>
          <Text className={styles.selectedFileName}>{fileName}</Text>
        </Flex>
      </Flex>
      <Button disabled={disabled} icon={<Trash2 size={17} />} onClick={onRemove} type="text" />
    </Flex>
  );
}
