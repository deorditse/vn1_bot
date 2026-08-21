import type {ReactNode} from 'react';

import {classNames} from '@shared/lib/classNames';
import styles from './AnimatedLoader.module.less';

type AnimatedLoaderProps = {
  action?: ReactNode;
  alt: string;
  description?: string;
  imageSrc: string;
  placement?: 'inline' | 'bottom';
  title: string;
};

export function AnimatedLoader({
  action,
  alt,
  description,
  imageSrc,
  placement = 'inline',
  title,
}: AnimatedLoaderProps) {
  return (
    <div
      aria-live="polite"
      className={classNames(styles.loader, {[styles.bottom]: placement === 'bottom'})}
      role="status"
    >
      <img alt={alt} src={imageSrc}/>
      <div className={styles.copy}>
        <strong>{title}</strong>
        {description ? <span>{description}</span> : null}
      </div>
      {action ? <div className={styles.action}>{action}</div> : null}
    </div>
  );
}
