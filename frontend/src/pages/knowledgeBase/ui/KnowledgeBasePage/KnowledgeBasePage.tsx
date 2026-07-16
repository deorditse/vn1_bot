import {Button, Input, Modal, Switch, Tag, Tooltip, Typography} from 'antd';
import {
    ArrowUp,
    Bot,
    Check,
    Copy,
    MessageSquareText,
    RefreshCw,
    RotateCcw,
    Settings2,
    SlidersHorizontal,
    Square,
    ThumbsDown,
    ThumbsUp,
    User,
} from 'lucide-react';
import {useEffect, useMemo, useRef, useState} from 'react';
import type {ReactNode} from 'react';

import {classNames} from '@shared/lib/classNames';
import {Card, HStack, VStack} from '@shared/ui';
import {Page} from '@widgets/Page';

import {
    type KnowledgeBaseChatSettings,
    loadKnowledgeBaseChatSettings,
    saveKnowledgeBaseChatSettings,
} from '../../model/settings';
import {useAvailableSkills} from '../../model/useAvailableSkills';
import {useKnowledgeBaseChat} from '../../model/useKnowledgeBaseChat';
import type {KnowledgeBaseChatMessage, ThinkingItem} from '../../model/useKnowledgeBaseChat';
import styles from './KnowledgeBasePage.module.less';

const {Text} = Typography;
const {TextArea} = Input;
type MessageReaction = 'like' | 'dislike';

const KnowledgeBasePage = () => {
    const initialSettings = useMemo(() => loadKnowledgeBaseChatSettings(), []);
    const [settings, setSettings] = useState<KnowledgeBaseChatSettings>(initialSettings);
    const [settingsModalOpen, setSettingsModalOpen] = useState(false);
    const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
    const [messageReactions, setMessageReactions] = useState<Record<string, MessageReaction | undefined>>({});
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const {error: skillsError, isLoading: isSkillsLoading, reload, skills} = useAvailableSkills();
    const {
        canSend,
        input,
        isStreaming,
        messages,
        reset,
        setInput,
        stop,
        submit,
    } = useKnowledgeBaseChat(settings);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({block: 'end'});
    }, [messages]);

    useEffect(() => {
        if (skills.some((skill) => skill.id === settings.skillId)) {
            return;
        }

        const nextSkillId = skills[0]?.id;
        if (nextSkillId) {
            updateSettings({skillId: nextSkillId});
        }
    }, [settings.skillId, skills]);

    const updateSettings = (patch: Partial<KnowledgeBaseChatSettings>) => {
        setSettings((prev) => {
            const next = {...prev, ...patch};
            saveKnowledgeBaseChatSettings(next);
            return next;
        });
    };
    const selectedSkill = skills.find((skill) => skill.id === settings.skillId);
    const isEmpty = messages.length === 0;
    const statusText = isStreaming
        ? 'Поток активен'
        : `${selectedSkill?.name || settings.skillId} · ${
            settings.searchMode === 'deep' ? 'глубокий режим' : 'сбалансированный режим'
        }${settings.includeSources ? ' · с источниками' : ''}`;

    return (
        <Page className={styles.page}>
            <section className={styles.chatShell}>
                <div className={styles.messages}>
                    <div className={styles.messagesInner}>
                        {isEmpty ? (
                            <EmptyChat
                                selectedSkillName={selectedSkill?.name || settings.skillId}
                            />
                        ) : null}
                        {messages.map((message) => (
                            <ChatMessage
                                copied={copiedMessageId === message.id}
                                key={message.id}
                                message={message}
                                onCopy={() => {
                                    void copyMessage(message, setCopiedMessageId);
                                }}
                                onReact={(reaction) => {
                                    setMessageReactions((prev) => ({
                                        ...prev,
                                        [message.id]: prev[message.id] === reaction ? undefined : reaction,
                                    }));
                                }}
                                reaction={messageReactions[message.id]}
                            />
                        ))}
                        <div ref={messagesEndRef}/>
                    </div>
                </div>

                <Card className={styles.composerCard} padding="12">
                    <VStack align="start" gap="8" max>
                        <TextArea
                            autoSize={{minRows: 2, maxRows: 6}}
                            className={styles.composerInput}
                            disabled={isStreaming}
                            onChange={(event) => setInput(event.target.value)}
                            onKeyDown={(event) => {
                                if (event.key === 'Enter' && !event.shiftKey) {
                                    event.preventDefault();
                                    void submit();
                                }
                            }}
                            placeholder="Введите вопрос по базе знаний"
                            value={input}
                        />
                        <HStack className={styles.composerActions} justify="between" max>
                            <HStack className={styles.composerStatus} gap="8">
                                <Tooltip title="Настройки">
                                    <Button
                                        aria-label="Настройки чата"
                                        icon={<Settings2 size={17}/>}
                                        onClick={() => setSettingsModalOpen(true)}
                                        type="text"
                                    />
                                </Tooltip>
                                <button
                                    className={styles.statusButton}
                                    onClick={() => setSettingsModalOpen(true)}
                                    type="button"
                                >
                                    <span className={classNames(styles.liveDot, {[styles.liveDotActive]: isStreaming})}/>
                                    <Text>{statusText}</Text>
                                </button>
                            </HStack>
                            <HStack className={styles.senderActions} gap="8">
                                <Tooltip title="Новый диалог">
                                    <Button
                                        aria-label="Новый диалог"
                                        icon={<RotateCcw size={17}/>}
                                        onClick={reset}
                                        type="text"
                                    />
                                </Tooltip>
                                {isStreaming ? (
                                    <Button icon={<Square size={16}/>} onClick={stop}>
                                        Остановить
                                    </Button>
                                ) : (
                                    <Button
                                        disabled={!canSend}
                                        icon={<ArrowUp size={17}/>}
                                        onClick={() => void submit()}
                                        type="primary"
                                    >
                                        Отправить
                                    </Button>
                                )}
                            </HStack>
                        </HStack>
                    </VStack>
                </Card>
            </section>

            <Modal
                className={styles.settingsModal}
                footer={null}
                onCancel={() => setSettingsModalOpen(false)}
                open={settingsModalOpen}
                centered
                title={(
                    <HStack gap="8">
                        <SlidersHorizontal size={18}/>
                        <span>Параметры запроса</span>
                    </HStack>
                )}
                width="min(720px, calc(100vw - 32px))"
            >
                <VStack align="start" gap="16" max>
                    <div className={styles.settingsSummary}>
                        <Text strong>{selectedSkill?.name || settings.skillId}</Text>
                        <Text>
                            {settings.searchMode === 'deep' ? 'Глубокий поиск' : 'Сбалансированный поиск'}
                            {settings.includeSources ? ' · источники включены' : ' · без источников'}
                        </Text>
                    </div>
                    <SettingField title="Навык">
                        <div className={styles.optionGrid}>
                            {skills.map((skill) => (
                                <button
                                    className={classNames(styles.optionCard, {
                                        [styles.optionCardActive]: settings.skillId === skill.id,
                                    })}
                                    disabled={isSkillsLoading}
                                    key={skill.id}
                                    onClick={() => updateSettings({skillId: skill.id})}
                                    type="button"
                                >
                                    <span>{skill.name || skill.id}</span>
                                    {skill.description ? <small>{skill.description}</small> : null}
                                </button>
                            ))}
                        </div>
                    </SettingField>
                    <SettingField title="Режим">
                        <div className={styles.optionGrid}>
                            <button
                                className={classNames(styles.optionCard, {
                                    [styles.optionCardActive]: settings.searchMode === 'balanced',
                                })}
                                onClick={() => updateSettings({searchMode: 'balanced'})}
                                type="button"
                            >
                                <span>Сбалансированный</span>
                                <small>Быстрый ответ для обычных запросов</small>
                            </button>
                            <button
                                className={classNames(styles.optionCard, {
                                    [styles.optionCardActive]: settings.searchMode === 'deep',
                                })}
                                onClick={() => updateSettings({searchMode: 'deep'})}
                                type="button"
                            >
                                <span>Глубокий</span>
                                <small>Больше времени на поиск и проверку</small>
                            </button>
                        </div>
                    </SettingField>
                    <SettingField title="Источники">
                        <div className={styles.switchRow}>
                            <div>
                                <Text strong>Показывать источники</Text>
                                <Text>Добавлять ссылки и найденные артефакты в ответ.</Text>
                            </div>
                            <Switch
                                checked={settings.includeSources}
                                checkedChildren="Вкл"
                                onChange={(checked) => updateSettings({includeSources: checked})}
                                unCheckedChildren="Выкл"
                            />
                        </div>
                    </SettingField>
                    <HStack className={styles.skillsMeta} justify="between" max>
                        <Text>{skillsError || `Доступно навыков: ${skills.length}`}</Text>
                        <Button icon={<RefreshCw size={16}/>} loading={isSkillsLoading} onClick={() => void reload()}>
                            Обновить
                        </Button>
                    </HStack>
                </VStack>
            </Modal>
        </Page>
    );
};

function EmptyChat({selectedSkillName}: {selectedSkillName: string}) {
    return (
        <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>
                <MessageSquareText size={24}/>
            </span>
            <div className={styles.emptyCopy}>
                <h1>База знаний</h1>
                <p>
                    Задайте вопрос, а ход обработки и итоговый ответ появятся в этом диалоге.
                    Сейчас выбран навык: {selectedSkillName}.
                </p>
            </div>
        </div>
    );
}

function SettingField({children, title}: {children: ReactNode; title: string}) {
    return (
        <div className={styles.settingField}>
            <Text strong>{title}</Text>
            {children}
        </div>
    );
}

function ChatMessage({
    copied,
    message,
    onCopy,
    onReact,
    reaction,
}: {
    copied: boolean;
    message: KnowledgeBaseChatMessage;
    onCopy: () => void;
    onReact: (reaction: MessageReaction) => void;
    reaction?: MessageReaction;
}) {
    const isUser = message.role === 'user';
    const messageSkills = message.skills?.length ? message.skills : message.skill ? [message.skill] : [];
    const canReact = !isUser && message.status !== 'streaming';

    return (
        <article className={classNames(styles.messageRow, {[styles.messageRowUser]: isUser})}>
            <span className={classNames(styles.avatar, {[styles.userAvatar]: isUser})}>
                {isUser ? <User size={18}/> : <Bot size={18}/>}
            </span>
            <div className={classNames(styles.messageBubble, {[styles.userBubble]: isUser})}>
                <HStack className={styles.messageMeta} gap="8" wrap="wrap">
                    <Text strong>{isUser ? 'Вы' : 'База знаний'}</Text>
                    {messageSkills.map((skill) => <Tag key={skill}>{skill}</Tag>)}
                    {message.status === 'streaming' ? <Tag color="processing">SSE</Tag> : null}
                    {message.status === 'error' ? <Tag color="error">Ошибка</Tag> : null}
                </HStack>

                {message.thinking?.length ? (
                    <details className={styles.thinkingTile} open={message.status === 'streaming'}>
                        <summary>
                            <span>Размышления</span>
                            <HStack gap="6">
                                <Text>{message.status === 'streaming' ? 'в процессе' : 'свернуто'}</Text>
                                <Tag>{message.thinking.length}</Tag>
                            </HStack>
                        </summary>
                        <VStack align="start" className={styles.thinkingList} gap="8" max>
                            {message.thinking.map((item) => (
                                <ThinkingStep item={item} key={`${message.id}-thinking-${item.id}`}/>
                            ))}
                        </VStack>
                    </details>
                ) : null}

                {message.content ? (
                    <div className={styles.messageText}>{message.content}</div>
                ) : (
                    <span className={styles.typingDots} aria-label="Ожидаю ответ">
                        <i/>
                        <i/>
                        <i/>
                    </span>
                )}
                <HStack className={styles.messageActions} gap="4">
                    <Tooltip title={copied ? 'Скопировано' : 'Копировать'}>
                        <Button
                            aria-label={copied ? 'Скопировано' : 'Копировать сообщение'}
                            icon={copied ? <Check size={15}/> : <Copy size={15}/>}
                            onClick={onCopy}
                            type="text"
                        />
                    </Tooltip>
                    {canReact ? (
                        <>
                            <Tooltip title="Лайк">
                                <Button
                                    aria-label="Лайк"
                                    className={classNames('', {[styles.messageActionActive]: reaction === 'like'})}
                                    icon={<ThumbsUp size={15}/>}
                                    onClick={() => onReact('like')}
                                    type="text"
                                />
                            </Tooltip>
                            <Tooltip title="Дизлайк">
                                <Button
                                    aria-label="Дизлайк"
                                    className={classNames('', {[styles.messageActionActive]: reaction === 'dislike'})}
                                    icon={<ThumbsDown size={15}/>}
                                    onClick={() => onReact('dislike')}
                                    type="text"
                                />
                            </Tooltip>
                        </>
                    ) : null}
                </HStack>
            </div>
        </article>
    );
}

function ThinkingStep({item}: {item: ThinkingItem}) {
    return (
        <div className={styles.thinkingStep}>
            <HStack className={styles.thinkingStepMeta} gap="6" wrap="wrap">
                {item.step ? <Tag>{formatStepName(item.step)}</Tag> : null}
                {item.status && item.status !== 'success' ? (
                    <Tag color={item.status === 'error' ? 'error' : 'default'}>{formatStatus(item.status)}</Tag>
                ) : null}
                {typeof item.duration_s === 'number' ? <Text>{formatDuration(item.duration_s)}</Text> : null}
            </HStack>
            <div className={styles.thinkingStepContent}>{stripMarkdownHeading(item.content)}</div>
        </div>
    );
}

function stripMarkdownHeading(content: string) {
    return content.replace(/^#{1,6}\s+/gm, '').trim();
}

function formatStepName(step: string) {
    const labels: Record<string, string> = {
        build_response: 'Ответ',
        search_gitlab: 'Поиск',
        validate_request: 'Проверка',
    };
    return labels[step] ?? step.replaceAll('_', ' ');
}

function formatStatus(status: string) {
    const labels: Record<string, string> = {
        error: 'ошибка',
        in_progress: 'идёт',
        success: 'готово',
    };
    return labels[status] ?? status;
}

function formatDuration(durationS: number) {
    if (durationS < 1) {
        return `${Math.round(durationS * 1000)} мс`;
    }
    return `${durationS.toFixed(1)} с`;
}

async function copyMessage(
    message: KnowledgeBaseChatMessage,
    setCopiedMessageId: (messageId: string | null) => void,
) {
    const text = message.content.trim();
    if (!text) {
        return;
    }

    await navigator.clipboard.writeText(text);
    setCopiedMessageId(message.id);
    window.setTimeout(() => setCopiedMessageId(null), 1400);
}

export default KnowledgeBasePage;
