import {createElement, forwardRef, type HTMLAttributes, type ReactNode} from 'react';

import {classNames} from '@shared/lib/classNames';

import styles from './Box.module.less';

export type BoxSpacing = '0' | '4' | '6' | '8' | '10' | '12' | '14' | '16' | '18' | '20' | '22' | '24' | '28' | '32';
export type BoxInlineSpacing = '8' | '12' | '16' | '18' | '24';
export type BoxBlockSpacing = '8' | '12' | '16' | '18' | '24';
export type BoxMargin = '0' | '4' | '8' | '12' | '16' | '24';
export type BoxMarginSide = '8' | '12' | '16' | '24';
export type BoxElement = 'div' | 'main' | 'section' | 'article' | 'aside' | 'header' | 'footer';

type BoxProps = HTMLAttributes<HTMLElement> & {
  as?: BoxElement;
  children: ReactNode;
  className?: string;
  max?: boolean;
  padding?: BoxSpacing;
  paddingX?: BoxInlineSpacing;
  paddingY?: BoxBlockSpacing;
  margin?: BoxMargin;
  marginTop?: BoxMarginSide;
  marginBottom?: BoxMarginSide;
};

const paddingClasses: Record<BoxSpacing, string> = {
  0: styles.p0,
  4: styles.p4,
  6: styles.p6,
  8: styles.p8,
  10: styles.p10,
  12: styles.p12,
  14: styles.p14,
  16: styles.p16,
  18: styles.p18,
  20: styles.p20,
  22: styles.p22,
  24: styles.p24,
  28: styles.p28,
  32: styles.p32,
};

const paddingXClasses: Record<BoxInlineSpacing, string> = {
  8: styles.px8,
  12: styles.px12,
  16: styles.px16,
  18: styles.px18,
  24: styles.px24,
};

const paddingYClasses: Record<BoxBlockSpacing, string> = {
  8: styles.py8,
  12: styles.py12,
  16: styles.py16,
  18: styles.py18,
  24: styles.py24,
};

const marginClasses: Record<BoxMargin, string> = {
  0: styles.m0,
  4: styles.m4,
  8: styles.m8,
  12: styles.m12,
  16: styles.m16,
  24: styles.m24,
};

const marginTopClasses: Record<BoxMarginSide, string> = {
  8: styles.mt8,
  12: styles.mt12,
  16: styles.mt16,
  24: styles.mt24,
};

const marginBottomClasses: Record<BoxMarginSide, string> = {
  8: styles.mb8,
  12: styles.mb12,
  16: styles.mb16,
  24: styles.mb24,
};

export const Box = forwardRef<HTMLElement, BoxProps>((props, ref) => {
  const {
    as: Component = 'div',
    children,
    className,
    max,
    padding,
    paddingX,
    paddingY,
    margin,
    marginTop,
    marginBottom,
    ...otherProps
  } = props;

  return createElement(
    Component,
    {
      className: classNames(
        styles.Box,
        {[styles.max]: max},
        [
          className,
          padding && paddingClasses[padding],
          paddingX && paddingXClasses[paddingX],
          paddingY && paddingYClasses[paddingY],
          margin && marginClasses[margin],
          marginTop && marginTopClasses[marginTop],
          marginBottom && marginBottomClasses[marginBottom],
        ],
      ),
      ...otherProps,
      ref,
    },
    children,
  );
});

Box.displayName = 'Box';
