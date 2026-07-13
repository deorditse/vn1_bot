export enum AppRoutes {
  ROOT = 'root',
  LOGIN = 'login',
}

export enum ToolRoutes {
  INSTRUCTION = 'instruction',
  KNOWLEDGE_BASE = 'knowledge-base',
}

export const getRouteRoot = () => '/';
export const getRouteLogin = () => '/login';
export const getRouteInstruction = () => '/instruction';
export const getRouteKnowledgeBase = () => '/knowledge-base';
