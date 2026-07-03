import {Button, Form, Input} from 'antd';
import {Lock, User} from 'lucide-react';

import styles from './LoginForm.module.less';

export type LoginFormValues = {
    username: string;
    password: string;
};

type LoginFormProps = {
    isSubmitting: boolean;
    onFinish: (values: LoginFormValues) => void;
};

export function LoginForm({isSubmitting, onFinish}: LoginFormProps) {
    return (
        <Form<LoginFormValues> className={styles.form} layout="vertical" onFinish={onFinish} requiredMark={false}>
            <Form.Item label="Логин" name="username" rules={[{message: 'Введите логин', required: true}]}>
                <Input autoComplete="username" prefix={<User size={17}/>} size="large"/>
            </Form.Item>

            <Form.Item label="Пароль" name="password" rules={[{message: 'Введите пароль', required: true}]}>
                <Input.Password autoComplete="current-password" prefix={<Lock size={17}/>} size="large"/>
            </Form.Item>

            <Button block htmlType="submit" loading={isSubmitting} size="large" type="primary">
                Войти
            </Button>
        </Form>
    );
}
