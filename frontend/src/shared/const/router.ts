export enum AppRoutes {
  ROOT = 'root',
  LOGIN = 'login',
}

export enum ToolRoutes {
  INSTRUCTION = 'instruction',
  DESCRIPTION_GENERATOR = 'description-generator',
  KNOWLEDGE_BASE = 'knowledge-base',
}

export const getRouteRoot = () => '/';
export const getRouteLogin = () => '/login';
export const getRouteInstruction = () => '/instruction';
export const getRouteDescriptionGenerator = () => '/description-generator';
export const getRouteKnowledgeBase = () => '/knowledge-base';
