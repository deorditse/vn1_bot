import { Navigate } from 'react-router-dom';
import { FileText } from 'lucide-react';

import { AppLayout } from '@app/layout/AppLayout';
import { InstructionPage } from '@pages/instruction';
import { LoginPage } from '@pages/login';
import {
  AppRoutes,
  ToolRoutes,
  getRouteInstruction,
  getRouteLogin,
  getRouteRoot,
} from '@shared/const/router';
import type { AppRoutesProps } from '@shared/types/router';

export const toolRouteConfig: Record<ToolRoutes, AppRoutesProps> = {
  [ToolRoutes.INSTRUCTION]: {
    path: getRouteInstruction(),
    element: <InstructionPage />,
    authOnly: true,
    nav: {
      label: 'Instruction',
      description: 'DOCX to HTML txt',
      icon: <FileText size={18} />,
    },
  },
};

const toolRoutes = Object.values(toolRouteConfig);

export const routeConfig: Record<AppRoutes, AppRoutesProps> = {
  [AppRoutes.LOGIN]: {
    path: getRouteLogin(),
    element: <LoginPage />,
  },
  [AppRoutes.ROOT]: {
    path: getRouteRoot(),
    element: <AppLayout />,
    authOnly: true,
    children: [
      {
        path: '',
        index: true,
        element: <Navigate replace to={getRouteInstruction().slice(1)} />,
      },
      ...toolRoutes,
      {
        path: '*',
        element: <Navigate replace to={getRouteInstruction()} />,
      },
    ],
  },
};

export const defaultAppRoute = toolRouteConfig[ToolRoutes.INSTRUCTION];
export const navRoutes = toolRoutes;
