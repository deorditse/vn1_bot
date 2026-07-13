import {useCallback, useEffect, useMemo, useState} from 'react';

import {AUTH_REQUIRED_EVENT} from '@shared/api';

export type AvailableSkill = {
    id: string;
    name: string;
    description?: string;
    required_roles?: string[];
};

type SkillsResponse = {
    skills?: AvailableSkill[];
};

const fallbackSkills: AvailableSkill[] = [
    {
        id: 'product_kb',
        name: 'База знаний',
        description: 'Поиск по базе знаний',
    },
    {
        id: 'orchestrator',
        name: 'Оркестратор',
        description: 'Выбор подходящих навыков',
    },
];

export function useAvailableSkills() {
    const [skills, setSkills] = useState<AvailableSkill[]>(fallbackSkills);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${__API_BASE_URL__}/skills/available`, {
                credentials: 'include',
                headers: {
                    Accept: 'application/json',
                },
            });

            if (response.status === 401) {
                window.dispatchEvent(new Event(AUTH_REQUIRED_EVENT));
                throw new Error('Требуется авторизация.');
            }

            if (!response.ok) {
                throw new Error('Не удалось получить список навыков.');
            }

            const payload = await response.json() as SkillsResponse;
            const nextSkills = payload.skills?.length ? payload.skills : fallbackSkills;
            setSkills(nextSkills);
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : 'Не удалось получить список навыков.');
            setSkills(fallbackSkills);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    const skillOptions = useMemo(
        () => skills.map((skill) => ({
            label: skill.name || skill.id,
            value: skill.id,
        })),
        [skills],
    );

    return {
        error,
        isLoading,
        reload: load,
        skillOptions,
        skills,
    };
}
