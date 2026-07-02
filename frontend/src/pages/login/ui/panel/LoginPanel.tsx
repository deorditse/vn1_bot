import {Alert, Typography} from 'antd';
import type {ReactNode} from 'react';

import {Card, VStack} from '@shared/ui';
import {LoginBrand} from '../brand/LoginBrand';
import styles from './LoginPanel.module.less';

const {Title} = Typography;

type LoginPanelProps = {
  children: ReactNode;
  error: string | null;
};

export function LoginPanel({children, error}: LoginPanelProps) {
  return (
    <Card className={styles.panel} padding="28">
      <VStack gap="22" max>
      <LoginBrand />

      <div className={styles.header}>
        <Title level={1}>Авторизация</Title>
      </div>

      {error && <Alert message={error} showIcon type="error" />}

      {children}
      </VStack>
    </Card>
  );
}
