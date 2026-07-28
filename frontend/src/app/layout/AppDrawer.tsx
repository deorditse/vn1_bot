import {Button, Drawer, Dropdown, Menu} from 'antd';
import type {MenuProps} from 'antd';
import {ChevronDown, ChevronLeft, LogOut} from 'lucide-react';
import {useMemo} from 'react';

import tabletkaLogo from '@shared/assets/tabletka-logo.svg';
import {navRoutes} from '../router/config/routeConfig';
import styles from './AppLayout.module.less';

const DRAWER_WIDTH = 328;

type AppDrawerProps = {
    activePath: string;
    onClose: () => void;
    onLogout: () => void;
    onSelectPath: (path: string) => void;
    open: boolean;
    profileName: string;
};

export function AppDrawer({activePath, onClose, onLogout, onSelectPath, open, profileName}: AppDrawerProps) {
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

    const profileMenuItems = useMemo<MenuProps['items']>(
        () => [
            {
                key: 'logout',
                danger: true,
                icon: <LogOut size={16}/>,
                label: 'Выйти',
                onClick: onLogout,
            },
        ],
        [onLogout],
    );

    const selectTool: MenuProps['onClick'] = ({key}) => {
        onSelectPath(String(key));
        onClose();
    };

    return (
        <Drawer
            className={styles.drawerPanel}
            closable={false}
            mask={false}
            onClose={onClose}
            open={open}
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
                    onClick={onClose}
                    type="text"
                />
            </div>
            <Menu
                className={styles.menu}
                items={menuItems}
                mode="inline"
                onClick={selectTool}
                selectedKeys={[activePath]}
            />
            <div className={styles.profilePanel}>
                <Dropdown
                    menu={{items: profileMenuItems}}
                    placement="topLeft"
                    trigger={['click']}
                >
                    <Button className={styles.profileButton} type="text">
                        <span>Профиль</span>
                        <ChevronDown size={16}/>
                    </Button>
                </Dropdown>
            </div>
        </Drawer>
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
