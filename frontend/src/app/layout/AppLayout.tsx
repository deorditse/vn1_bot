import {Button, Layout, Typography} from 'antd';
import {Menu as MenuIcon} from 'lucide-react';
import {useState} from 'react';
import {Outlet, useLocation, useNavigate} from 'react-router-dom';

import {useAuth} from '@features/auth';
import {classNames} from '@shared/lib/classNames';
import {defaultAppRoute, navRoutes} from '../router/config/routeConfig';
import {AppDrawer} from './AppDrawer';
import styles from './AppLayout.module.less';

const {Header} = Layout;
const {Text, Title} = Typography;

export function AppLayout() {
    const [drawerOpen, setDrawerOpen] = useState(true);
    const {signOut, user} = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const active = navRoutes.find((route) => route.path === location.pathname) ?? defaultAppRoute;
    const username = user && 'username' in user ? user.username : undefined;
    const email = user && 'email' in user ? user.email : undefined;
    const profileName = username || email || 'Профиль';

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
                    <div className={styles.pageIcon}>{active.nav?.icon}</div>
                    <div className={styles.titleBlock}>
                        <Title level={1}>{active.nav?.label}</Title>
                        {active.nav?.description ? <Text>{active.nav.description}</Text> : null}
                    </div>
                </Header>

                <div className={styles.content}><Outlet/></div>


            </Layout>

            <AppDrawer
                activePath={active.path}
                onClose={() => setDrawerOpen(false)}
                onLogout={logout}
                onSelectPath={(path) => navigate(path)}
                open={drawerOpen}
                profileName={profileName}
            />
        </Layout>
    );
}
