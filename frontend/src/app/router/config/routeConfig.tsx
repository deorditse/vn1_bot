import { Navigate } from 'react-router-dom';
import { BookOpen, FileSpreadsheet, FileText } from 'lucide-react';

import { AppLayout } from '@app/layout/AppLayout';
import { InstructionPage } from '@pages/instruction';
import { DescriptionGeneratorPage } from '@pages/descriptionGenerator';
import { KnowledgeBasePage } from '@pages/knowledgeBase';
import { LoginPage } from '@pages/login';
import {
  AppRoutes,
  ToolRoutes,
  getRouteDescriptionGenerator,
  getRouteInstruction,
  getRouteKnowledgeBase,
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
      label: 'Инструкции',
      description: 'DOCX → HTML и краткое описание',
      icon: <FileText size={18} />,
    },
  },
  [ToolRoutes.DESCRIPTION_GENERATOR]: {
    path: getRouteDescriptionGenerator(),
    element: <DescriptionGeneratorPage />,
    authOnly: true,
    nav: {
      label: 'Описания товаров',
      description: 'Разметка → готовая таблица',
      icon: <FileSpreadsheet size={18} />,
    },
  },
  [ToolRoutes.KNOWLEDGE_BASE]: {
    path: getRouteKnowledgeBase(),
    element: <KnowledgeBasePage />,
    authOnly: true,
    nav: {
      label: 'База знаний',
      description: 'Поиск по внутренним источникам',
      icon: <BookOpen size={18} />,
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
