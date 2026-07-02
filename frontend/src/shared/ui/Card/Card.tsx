import {memo, type HTMLAttributes, type ReactNode} from 'react';

import {classNames} from '@shared/lib/classNames';

import styles from './Card.module.less';

export type CardVariant = 'normal' | 'outlined' | 'light';
export type CardPadding = '0' | '8' | '12' | '16' | '18' | '22' | '24' | '28';
export type CardBorder = 'round' | 'normal' | 'partial';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
  children: ReactNode;
  variant?: CardVariant;
  max?: boolean;
  padding?: CardPadding;
  border?: CardBorder;
  fullWidth?: boolean;
  fullHeight?: boolean;
}

const mapPaddingToClass: Record<CardPadding, string> = {
  0: styles.padding0,
  8: styles.padding8,
  12: styles.padding12,
  16: styles.padding16,
  18: styles.padding18,
  22: styles.padding22,
  24: styles.padding24,
  28: styles.padding28,
};

const mapBorderToClass: Record<CardBorder, string> = {
  round: styles.round,
  normal: styles.normalBorder,
  partial: styles.partial,
};

export const Card = memo((props: CardProps) => {
  const {
    className,
    children,
    variant = 'normal',
    max,
    padding = '8',
    border = 'normal',
    fullWidth,
    fullHeight,
    ...otherProps
  } = props;

  return (
    <div
      className={classNames(
        styles.Card,
        {
          [styles.max]: max,
          [styles.fullHeight]: fullHeight,
          [styles.fullWidth]: fullWidth,
        },
        [className, styles[variant], mapPaddingToClass[padding], mapBorderToClass[border]],
      )}
      {...otherProps}
    >
      {children}
    </div>
  );
});
