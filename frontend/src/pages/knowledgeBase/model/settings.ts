export type KnowledgeBaseSkillId = string;
export type KnowledgeBaseSearchMode = 'balanced' | 'deep';

export type KnowledgeBaseChatSettings = {
    skillId: KnowledgeBaseSkillId;
    searchMode: KnowledgeBaseSearchMode;
    includeSources: boolean;
};

const STORAGE_KEY = 'vn1:knowledge-base-chat-settings';

export const defaultKnowledgeBaseChatSettings: KnowledgeBaseChatSettings = {
    skillId: 'product_kb',
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
        return {
            ...defaultKnowledgeBaseChatSettings,
            ...parsed,
            skillId: parsed.skillId === 'orchestrator' ? 'orchestrator' : 'product_kb',
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
