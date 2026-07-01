import {memo, type ReactNode, useEffect, useRef} from 'react';

import {classNames} from '@shared/lib/classNames';

import styles from './Page.module.less';

type PageProps = {
    className?: string;
    children: ReactNode;
    onScrollEnd?: () => void;
    'data-testid'?: string;
};

export const PAGE_ID = 'PAGE_ID';

export const Page = memo((props: PageProps) => {
    const {className, children, onScrollEnd} = props;
    const wrapperRef = useRef<HTMLElement | null>(null);
    const triggerRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const trigger = triggerRef.current;

        if (!onScrollEnd || !trigger) return undefined;


        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    onScrollEnd();
                }
            },
            {
                root: wrapperRef.current,
            },
        );

        observer.observe(trigger);

        return () => {
            observer.disconnect();
        };
    }, [onScrollEnd]);

    return (
        <main
            className={classNames(styles.Page, {}, [className])}
            data-testid={props['data-testid'] ?? 'Page'}
            id={PAGE_ID}
            ref={wrapperRef}
        >
            {children}
            {onScrollEnd ? <div className={styles.trigger} ref={triggerRef}/> : null}
        </main>
    );
});
