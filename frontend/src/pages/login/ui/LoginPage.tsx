import { Alert, Button, Form, Input, Typography } from 'antd';
import { FileCode2, Lock, User } from 'lucide-react';
import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '@features/auth/model/AuthProvider';
import { getRouteInstruction } from '@shared/const/router';
import styles from './LoginPage.module.less';

const { Text, Title } = Typography;

type LoginForm = {
  username: string;
  password: string;
};

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const { isAuthenticated, signIn } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as LocationState | null)?.from?.pathname ?? getRouteInstruction();

  if (isAuthenticated) {
    return <Navigate replace to={from} />;
  }

  const onFinish = async (values: LoginForm) => {
    setError(null);
    setIsSubmitting(true);

    try {
      await signIn(values.username, values.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось выполнить вход');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className={styles.page}>
      <section className={styles.panel}>
        <div className={styles.brand}>
          <span>
            <FileCode2 size={22} />
          </span>
          <div>
            <strong>VN1 Bot</strong>
            <small>Keycloak sign in</small>
          </div>
        </div>

        <div className={styles.header}>
          <Text className={styles.kicker}>Protected workspace</Text>
          <Title level={1}>Авторизация</Title>
        </div>

        {error && <Alert message={error} showIcon type="error" />}

        <Form<LoginForm> className={styles.form} layout="vertical" onFinish={onFinish} requiredMark={false}>
          <Form.Item
            label="Логин"
            name="username"
            rules={[{ message: 'Введите логин', required: true }]}
          >
            <Input autoComplete="username" prefix={<User size={17} />} size="large" />
          </Form.Item>

          <Form.Item
            label="Пароль"
            name="password"
            rules={[{ message: 'Введите пароль', required: true }]}
          >
            <Input.Password autoComplete="current-password" prefix={<Lock size={17} />} size="large" />
          </Form.Item>

          <Button block htmlType="submit" loading={isSubmitting} size="large" type="primary">
            Войти
          </Button>
        </Form>
      </section>
    </main>
  );
}
