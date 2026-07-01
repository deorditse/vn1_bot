import {Alert, Typography} from 'antd';
import type {ReactNode} from 'react';

import {LoginBrand} from '../brand/LoginBrand';
import styles from './LoginPanel.module.less';

const {Title} = Typography;

type LoginPanelProps = {
  children: ReactNode;
  error: string | null;
};

export function LoginPanel({children, error}: LoginPanelProps) {
  return (
    <section className={styles.panel}>
      <LoginBrand />

      <div className={styles.header}>
        <Title level={1}>Авторизация</Title>
      </div>

      {error && <Alert message={error} showIcon type="error" />}

      {children}
    </section>
  );
}
