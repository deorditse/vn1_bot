import type {DetailedHTMLProps, HTMLAttributes, ReactNode} from 'react';

import {classNames, type Mods} from '@shared/lib/classNames';

import styles from './Flex.module.less';

export type FlexJustify = 'start' | 'center' | 'end' | 'between';
export type FlexAlign = 'start' | 'center' | 'end';
export type FlexDirection = 'row' | 'column';
export type FlexWrap = 'nowrap' | 'wrap';
export type FlexGap = '4' | '6' | '8' | '10' | '12' | '14' | '16' | '18' | '20' | '22' | '24' | '28' | '32';

const justifyClasses: Record<FlexJustify, string> = {
  start: styles.justifyStart,
  center: styles.justifyCenter,
  end: styles.justifyEnd,
  between: styles.justifyBetween,
};

const alignClasses: Record<FlexAlign, string> = {
  start: styles.alignStart,
  center: styles.alignCenter,
  end: styles.alignEnd,
};

const directionClasses: Record<FlexDirection, string> = {
  row: styles.directionRow,
  column: styles.directionColumn,
};

const gapClasses: Record<FlexGap, string> = {
  4: styles.gap4,
  6: styles.gap6,
  8: styles.gap8,
  10: styles.gap10,
  12: styles.gap12,
  14: styles.gap14,
  16: styles.gap16,
  18: styles.gap18,
  20: styles.gap20,
  22: styles.gap22,
  24: styles.gap24,
  28: styles.gap28,
  32: styles.gap32,
};

type DivProps = DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>;

export interface FlexProps extends DivProps {
  className?: string;
  children: ReactNode;
  justify?: FlexJustify;
  align?: FlexAlign;
  direction: FlexDirection;
  wrap?: FlexWrap;
  gap?: FlexGap;
  max?: boolean;
}

export function Flex(props: FlexProps) {
  const {
    className,
    children,
    justify = 'start',
    align = 'center',
    direction = 'row',
    wrap = 'nowrap',
    gap,
    max,
    ...otherProps
  } = props;

  const classes = [
    className,
    justifyClasses[justify],
    alignClasses[align],
    directionClasses[direction],
    styles[wrap],
    gap && gapClasses[gap],
  ];

  const mods: Mods = {
    [styles.max]: max,
  };

  return (
    <div className={classNames(styles.Flex, mods, classes)} {...otherProps}>
      {children}
    </div>
  );
}
