import type { ReactNode } from 'react';

export type AppRoutesProps = {
  path: string;
  element: ReactNode;
  authOnly?: boolean;
  index?: boolean;
  children?: AppRoutesProps[];
  nav?: {
    label: string;
    description: string;
    icon: ReactNode;
  };
};
