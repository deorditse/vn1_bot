import {FileCode2} from 'lucide-react';

import styles from './LoginBrand.module.less';

export function LoginBrand() {
  return (
    <div className={styles.brand}>
      <span>
        <FileCode2 size={22} />
      </span>
      <div>
        <strong>TABLETKA</strong>
      </div>
    </div>
  );
}
