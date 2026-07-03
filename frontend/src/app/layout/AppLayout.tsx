import {Button, Drawer, Layout, Menu, Typography} from 'antd';
import type {MenuProps} from 'antd';
import {ChevronLeft, LogOut, Menu as MenuIcon} from 'lucide-react';
import {useMemo, useState} from 'react';
import {Outlet, useLocation, useNavigate} from 'react-router-dom';

import {useAuth} from '@features/auth';
import {classNames} from '@shared/lib/classNames';
import {VStack} from '@shared/ui';
import tabletkaLogo from '@shared/assets/tabletka-logo.svg';
import {defaultAppRoute, navRoutes} from '../router/config/routeConfig';
import styles from './AppLayout.module.less';

const {Header} = Layout;
const {Text, Title} = Typography;
const DRAWER_WIDTH = 328;

export function AppLayout() {
    const [drawerOpen, setDrawerOpen] = useState(true);
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
        navigate('/login', {replace: true});
    };

    return (
        <Layout className={classNames(styles.layout, {[styles.layoutDrawerOpen]: drawerOpen})}>
            <Button
                className={styles.drawerButton}
                icon={<MenuIcon size={20}/>}
                onClick={() => setDrawerOpen((prev) => !prev)}
                type="text"
            />
            <Layout className={styles.mainLayout}>
                <Header className={styles.topbar}>
                    <VStack className={styles.titleBlock} gap="4">
                        <Title level={1}>{active.nav?.label}</Title>
                        <Text className={styles.kicker}>{active.nav?.description}</Text>
                    </VStack>
                    <div className={styles.account}>
                        <Text>{username}</Text>
                        <Button icon={<LogOut size={18}/>} onClick={logout} type="text"/>

                    </div>
                </Header>

                <div className={styles.content}><Outlet/></div>


            </Layout>

            <Drawer
                className={styles.drawerPanel}
                closable={false}
                mask={false}
                onClose={() => setDrawerOpen(false)}
                open={drawerOpen}
                placement="left"
                rootClassName={styles.drawerRoot}
                title={null}
                width={DRAWER_WIDTH}
            >
                <div className={styles.drawerHead}>
                    <Brand/>
                    <Button
                        aria-label="Закрыть меню"
                        className={styles.drawerClose}
                        icon={<ChevronLeft size={20}/>}
                        onClick={() => setDrawerOpen(false)}
                        type="text"
                    />
                </div>
                <Menu
                    className={styles.menu}
                    items={menuItems}
                    mode="inline"
                    onClick={selectTool}
                    selectedKeys={[active.path]}
                />
            </Drawer>
        </Layout>
    );
}

function Brand() {
    return (
        <div className={styles.brand}>
            <img alt="Таблетка.ру" src={tabletkaLogo}/>
            <small>| Bot-api</small>
        </div>
    );
}
