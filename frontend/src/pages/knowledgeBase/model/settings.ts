export type KnowledgeBaseSkillId = string;
export type KnowledgeBaseSearchMode = 'balanced' | 'deep';

export type KnowledgeBaseChatSettings = {
    skillId: KnowledgeBaseSkillId;
    orchestratorSkillIds: KnowledgeBaseSkillId[];
    searchMode: KnowledgeBaseSearchMode;
    includeSources: boolean;
};

const STORAGE_KEY = 'vn1:knowledge-base-chat-settings';

export const defaultKnowledgeBaseChatSettings: KnowledgeBaseChatSettings = {
    skillId: 'orchestrator',
    orchestratorSkillIds: [],
    searchMode: 'balanced',
    includeSources: true,
};

export function loadKnowledgeBaseChatSettings(): KnowledgeBaseChatSettings {
    try {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            return defaultKnowledgeBaseChatSettings;
        }

        const parsed = JSON.parse(raw) as Partial<KnowledgeBaseChatSettings>;
        const skillId = typeof parsed.skillId === 'string' && parsed.skillId.trim()
            ? parsed.skillId
            : defaultKnowledgeBaseChatSettings.skillId;

        return {
            ...defaultKnowledgeBaseChatSettings,
            ...parsed,
            skillId,
            orchestratorSkillIds: Array.isArray(parsed.orchestratorSkillIds)
                ? parsed.orchestratorSkillIds.filter((item): item is string => typeof item === 'string' && Boolean(item))
                : defaultKnowledgeBaseChatSettings.orchestratorSkillIds,
            searchMode: parsed.searchMode === 'deep' ? 'deep' : 'balanced',
            includeSources: parsed.includeSources ?? defaultKnowledgeBaseChatSettings.includeSources,
        };
    } catch {
        return defaultKnowledgeBaseChatSettings;
    }
}

export function saveKnowledgeBaseChatSettings(settings: KnowledgeBaseChatSettings) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}
