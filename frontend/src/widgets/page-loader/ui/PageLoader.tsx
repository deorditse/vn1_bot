import { Spin } from 'antd';

import styles from './PageLoader.module.less';

export function PageLoader() {
  return (
    <div className={styles.loader}>
      <Spin size="large" />
    </div>
  );
}
