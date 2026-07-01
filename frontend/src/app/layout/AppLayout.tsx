import {Button, Drawer, Layout, Menu, Space, Typography} from 'antd';
import type {MenuProps} from 'antd';
import {FileCode2, LogOut, Menu as MenuIcon} from 'lucide-react';
import {useMemo, useState} from 'react';
import {Outlet, useLocation, useNavigate} from 'react-router-dom';

import {useAuth} from '@features/auth/model/AuthProvider';
import {isDevAuthDisabled} from '@shared/config/env';
import {defaultAppRoute, navRoutes} from '../router/config/routeConfig';
import styles from './AppLayout.module.less';

const {Content, Header, Sider} = Layout;
const {Text, Title} = Typography;

export function AppLayout() {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const {signOut, user} = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const active = navRoutes.find((route) => route.path === location.pathname) ?? defaultAppRoute;
    const username = user && 'username' in user ? user.username : undefined;

    const menuItems = useMemo<MenuProps['items']>(
        () =>
            navRoutes.map((route) => ({
                key: route.path,
                icon: route.nav?.icon,
                label: (
                    <div className={styles.menuLabel}>
                        <span>{route.nav?.label}</span>
                        <small>{route.nav?.description}</small>
                    </div>
                ),
            })),
        [],
    );

    const selectTool: MenuProps['onClick'] = ({key}) => {
        navigate(key);
        setDrawerOpen(false);
    };

    const logout = async () => {
        await signOut();
        if (isDevAuthDisabled) {
            return;
        }
        navigate('/login', {replace: true});
    };

    return (
        <Layout className={styles.layout}>
            <Sider className={styles.sider} width={292}>
                <Brand/>
                <Menu
                    className={styles.menu}
                    items={menuItems}
                    mode="inline"
                    onClick={selectTool}
                    selectedKeys={[active.path]}
                />
            </Sider>

            <Layout className={styles.mainLayout}>
                <Header className={styles.topbar}>
                    <Button
                        className={styles.drawerButton}
                        icon={<MenuIcon size={20}/>}
                        onClick={() => setDrawerOpen(true)}
                        type="text"
                    />
                    <Space className={styles.titleBlock} direction="vertical" size={0}>
                        <Title level={1}>{active.nav?.label}</Title>
                        <Text className={styles.kicker}>{active.nav?.description}</Text>
                    </Space>
                    <div className={styles.account}>
                        <Text>{username}</Text>
                        {!isDevAuthDisabled && <Button icon={<LogOut size={18}/>} onClick={logout} type="text"/>}
                    </div>
                </Header>

                <Content className={styles.content}>
                    <Outlet/>
                </Content>
            </Layout>

            <Drawer
                className={styles.drawer}
                onClose={() => setDrawerOpen(false)}
                open={drawerOpen}
                placement="left"
                title={<Brand/>}
                width={320}
            >
                <Menu items={menuItems} mode="inline" onClick={selectTool} selectedKeys={[active.path]}/>
            </Drawer>
        </Layout>
    );
}

function Brand() {
    return (
        <div className={styles.brand}>
      <span>
        <FileCode2 size={19}/>
      </span>
            <div>
                <strong>TABLETKA</strong>
                <small>Bot-api</small>
            </div>
        </div>
    );
}
