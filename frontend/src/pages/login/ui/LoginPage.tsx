import {useState} from 'react';
import {Navigate, useLocation, useNavigate} from 'react-router-dom';

import {useAuth} from '@features/auth/model/AuthProvider';
import {classNames} from '@shared/lib/classNames';
import {AppPaddings} from '@shared/lib/styles';
import {getRouteInstruction} from '@shared/const/router';
import {Page} from '@widgets/Page';
import {LoginForm} from './form/LoginForm';
import type {LoginFormValues} from './form/LoginForm';
import {LoginPanel} from './panel/LoginPanel';
import styles from './LoginPage.module.less';

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const {isAuthenticated, signIn} = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as LocationState | null)?.from?.pathname ?? getRouteInstruction();

  if (isAuthenticated) {
    return <Navigate replace to={from} />;
  }

  const onFinish = async (values: LoginFormValues) => {
    setError(null);
    setIsSubmitting(true);

    try {
      await signIn(values.username, values.password);
      navigate(from, {replace: true});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось выполнить вход');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Page className={classNames(styles.page, {}, [AppPaddings.p24])}>
      <LoginPanel error={error}>
        <LoginForm isSubmitting={isSubmitting} onFinish={onFinish} />
      </LoginPanel>
    </Page>
  );
}
