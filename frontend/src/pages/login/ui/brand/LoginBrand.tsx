import {FileCode2} from 'lucide-react';

import {HStack} from '@shared/ui';
import styles from './LoginBrand.module.less';

export function LoginBrand() {
  return (
    <HStack className={styles.brand} gap="12">
      <span>
        <FileCode2 size={22} />
      </span>
      <div>
        <strong>TABLETKA</strong>
      </div>
    </HStack>
  );
}
