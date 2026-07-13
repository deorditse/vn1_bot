import {useCallback, useMemo, useRef, useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';

import {AUTH_REQUIRED_EVENT} from '@shared/api';

import {parseSseMessages} from './sse';
import type {KnowledgeBaseChatSettings} from './settings';
import type {AvailableSkill} from './useAvailableSkills';

type ChatRole = 'user' | 'assistant';
type ChatStatus = 'idle' | 'streaming' | 'success' | 'error';

export type KnowledgeBaseChatMessage = {
    id: string;
    role: ChatRole;
    content: string;
    status: ChatStatus;
    skill?: string;
    thinking?: string[];
};

type FragmentPayload = {
    fragment_type?: string;
    status?: string;
    content?: string;
    streaming?: boolean;
    step?: string;
};

type FinalPayload = {
    id?: string;
    message_id?: string;
    data?: string;
    skill?: string;
    status?: string;
};

const initialMessages: KnowledgeBaseChatMessage[] = [
    {
        id: 'welcome',
        role: 'assistant',
        content: 'Задайте вопрос по базе знаний. Я покажу ход обработки и финальный ответ в одном диалоге.',
        status: 'success',
    },
];

export function useKnowledgeBaseChat(settings: KnowledgeBaseChatSettings, availableSkills: AvailableSkill[]) {
    const [messages, setMessages] = useState<KnowledgeBaseChatMessage[]>(initialMessages);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const chatIdRef = useRef(crypto.randomUUID());
    const abortRef = useRef<AbortController | null>(null);

    const canSend = useMemo(() => input.trim().length > 0 && !isStreaming, [input, isStreaming]);

    const submit = useCallback(async () => {
        const question = input.trim();
        if (!question || isStreaming) {
            return;
        }

        const userMessage: KnowledgeBaseChatMessage = {
            id: crypto.randomUUID(),
            role: 'user',
            content: question,
            status: 'success',
        };
        const assistantId = crypto.randomUUID();
        const assistantMessage: KnowledgeBaseChatMessage = {
            id: assistantId,
            role: 'assistant',
            content: '',
            status: 'streaming',
            thinking: [],
        };

        setMessages((prev) => [...prev, userMessage, assistantMessage]);
        setInput('');
        setIsStreaming(true);

        const controller = new AbortController();
        abortRef.current = controller;

        try {
            const response = await fetch(`${__API_BASE_URL__}/chat/stream`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'text/event-stream',
                },
                body: JSON.stringify({
                    chat_id: chatIdRef.current,
                    question,
                    skill_id: settings.skillId,
                    available_skills: settings.skillId === 'orchestrator'
                        ? availableSkills
                            .map((skill) => skill.id)
                            .filter((skillId) => skillId !== 'orchestrator')
                        : [],
                    context: {
                        search_mode: settings.searchMode,
                        include_sources: settings.includeSources,
                    },
                }),
                signal: controller.signal,
            });

            if (response.status === 401) {
                window.dispatchEvent(new Event(AUTH_REQUIRED_EVENT));
                throw new Error('Требуется авторизация.');
            }

            if (!response.ok || !response.body) {
                throw new Error('Не удалось открыть SSE-поток.');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const {done, value} = await reader.read();
                if (done) {
                    break;
                }

                buffer += decoder.decode(value, {stream: true});
                const parsed = parseSseMessages(buffer);
                buffer = parsed.rest;

                parsed.messages.forEach((message) => {
                    if (message.event === 'set') {
                        applyFinalMessage(assistantId, message.data as FinalPayload, setMessages);
                        return;
                    }

                    applyFragment(assistantId, message.data as FragmentPayload, setMessages);
                });
            }
        } catch (error) {
            if (!controller.signal.aborted) {
                const content = error instanceof Error ? error.message : 'Ошибка обработки запроса.';
                setMessages((prev) => updateAssistant(prev, assistantId, {content, status: 'error'}));
            }
        } finally {
            abortRef.current = null;
            setIsStreaming(false);
        }
    }, [availableSkills, input, isStreaming, settings]);

    const stop = useCallback(() => {
        abortRef.current?.abort();
        setIsStreaming(false);
    }, []);

    const reset = useCallback(() => {
        abortRef.current?.abort();
        chatIdRef.current = crypto.randomUUID();
        setMessages(initialMessages);
        setInput('');
        setIsStreaming(false);
    }, []);

    return {
        canSend,
        input,
        isStreaming,
        messages,
        reset,
        setInput,
        stop,
        submit,
    };
}

function applyFragment(
    assistantId: string,
    fragment: FragmentPayload,
    setMessages: Dispatch<SetStateAction<KnowledgeBaseChatMessage[]>>,
) {
    if (!fragment || typeof fragment.content !== 'string') {
        return;
    }
    const content = fragment.content;

    setMessages((prev) => {
        const message = prev.find((item) => item.id === assistantId);
        if (!message) {
            return prev;
        }

        if (fragment.fragment_type === 'response') {
            const nextContent = fragment.streaming ? `${message.content}${content}` : content;
            return updateAssistant(prev, assistantId, {
                content: nextContent,
                status: fragment.status === 'error' ? 'error' : 'streaming',
            });
        }

        return updateAssistant(prev, assistantId, {
            thinking: [...(message.thinking ?? []), content],
            status: fragment.status === 'error' ? 'error' : 'streaming',
        });
    });
}

function applyFinalMessage(
    assistantId: string,
    payload: FinalPayload,
    setMessages: Dispatch<SetStateAction<KnowledgeBaseChatMessage[]>>,
) {
    setMessages((prev) => updateAssistant(prev, assistantId, {
        id: payload.id ?? payload.message_id ?? assistantId,
        content: payload.data ?? '',
        skill: payload.skill,
        status: payload.status === 'error' ? 'error' : 'success',
    }));
}

function updateAssistant(
    messages: KnowledgeBaseChatMessage[],
    assistantId: string,
    patch: Partial<KnowledgeBaseChatMessage>,
) {
    return messages.map((message) => (
        message.id === assistantId
            ? {...message, ...patch}
            : message
    ));
}
