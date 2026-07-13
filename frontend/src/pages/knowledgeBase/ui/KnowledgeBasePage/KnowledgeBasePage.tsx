import {Button, Input, Modal, Radio, Switch, Tag, Tooltip, Typography} from 'antd';
import {ArrowUp, Bot, RefreshCw, RotateCcw, Settings2, SlidersHorizontal, Square, User} from 'lucide-react';
import {useEffect, useMemo, useState} from 'react';
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
import type {KnowledgeBaseChatMessage} from '../../model/useKnowledgeBaseChat';
import styles from './KnowledgeBasePage.module.less';

const {Text, Title} = Typography;
const {TextArea} = Input;

const KnowledgeBasePage = () => {
    const initialSettings = useMemo(() => loadKnowledgeBaseChatSettings(), []);
    const [settings, setSettings] = useState<KnowledgeBaseChatSettings>(initialSettings);
    const [settingsModalOpen, setSettingsModalOpen] = useState(false);
    const {error: skillsError, isLoading: isSkillsLoading, reload, skillOptions, skills} = useAvailableSkills();
    const {
        canSend,
        input,
        isStreaming,
        messages,
        reset,
        setInput,
        stop,
        submit,
    } = useKnowledgeBaseChat(settings, skills);

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

    return (
        <Page className={styles.page}>
            <section className={styles.chatShell}>
                <HStack className={styles.chatHeader} justify="between" max>
                    <Button icon={<RotateCcw size={17}/>} onClick={reset} type="text">
                        Новый диалог
                    </Button>
                </HStack>

                <div className={styles.messages}>
                    {messages.map((message) => (
                        <ChatMessage key={message.id} message={message}/>
                    ))}
                </div>

                <Card className={styles.composerCard} padding="12">
                    <VStack align="start" gap="10" max>
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
                                <span className={classNames(styles.liveDot, {[styles.liveDotActive]: isStreaming})}/>
                                <Text>
                                    {isStreaming
                                        ? 'Поток активен'
                                        : `${selectedSkill?.name || settings.skillId} · ${
                                            settings.searchMode === 'deep' ? 'глубокий' : 'сбалансированный'
                                        }`}
                                </Text>
                            </HStack>
                            <HStack className={styles.senderActions} gap="8">
                                <Tooltip title="Настройки">
                                    <Button
                                        aria-label="Настройки чата"
                                        icon={<Settings2 size={17}/>}
                                        onClick={() => setSettingsModalOpen(true)}
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
                title={(
                    <HStack gap="8">
                        <SlidersHorizontal size={18}/>
                        <span>Параметры запроса</span>
                    </HStack>
                )}
                width={720}
            >
                <VStack align="start" gap="18" max>
                    <SettingField title="Навык">
                        <Radio.Group
                            disabled={isSkillsLoading}
                            onChange={(event) => updateSettings({skillId: event.target.value})}
                            optionType="button"
                            options={skillOptions}
                            value={settings.skillId}
                        />
                    </SettingField>
                    <SettingField title="Режим">
                        <Radio.Group
                            onChange={(event) => updateSettings({searchMode: event.target.value})}
                            optionType="button"
                            options={[
                                {label: 'Сбалансированный', value: 'balanced'},
                                {label: 'Глубокий', value: 'deep'},
                            ]}
                            value={settings.searchMode}
                        />
                    </SettingField>
                    <SettingField title="Источники">
                        <Switch
                            checked={settings.includeSources}
                            checkedChildren="Вкл"
                            onChange={(checked) => updateSettings({includeSources: checked})}
                            unCheckedChildren="Выкл"
                        />
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

function SettingField({children, title}: {children: ReactNode; title: string}) {
    return (
        <div className={styles.settingField}>
            <Text strong>{title}</Text>
            {children}
        </div>
    );
}

function ChatMessage({message}: {message: KnowledgeBaseChatMessage}) {
    const isUser = message.role === 'user';

    return (
        <article className={classNames(styles.messageRow, {[styles.messageRowUser]: isUser})}>
            <span className={classNames(styles.avatar, {[styles.userAvatar]: isUser})}>
                {isUser ? <User size={18}/> : <Bot size={18}/>}
            </span>
            <div className={classNames(styles.messageBubble, {[styles.userBubble]: isUser})}>
                <HStack className={styles.messageMeta} gap="8" wrap="wrap">
                    <Text strong>{isUser ? 'Вы' : 'База знаний'}</Text>
                    {message.skill ? <Tag>{message.skill}</Tag> : null}
                    {message.status === 'streaming' ? <Tag color="processing">SSE</Tag> : null}
                    {message.status === 'error' ? <Tag color="error">Ошибка</Tag> : null}
                </HStack>

                {message.thinking?.length ? (
                    <VStack align="start" className={styles.thinking} gap="6" max>
                        {message.thinking.map((item, index) => (
                            <Text key={`${message.id}-thinking-${index}`}>{item}</Text>
                        ))}
                    </VStack>
                ) : null}

                {message.content ? (
                    <div className={styles.messageText}>{message.content}</div>
                ) : (
                    <Text className={styles.placeholder}>Ожидаю ответ...</Text>
                )}
            </div>
        </article>
    );
}

export default KnowledgeBasePage;
