import type {ReactNode, SyntheticEvent} from 'react';
import {Check, PackageCheck, Pill, Sparkles} from 'lucide-react';

import {VStack} from '@shared/ui';
import type {
    AiDescriptionProductType,
    GenerationOptions,
    NonMedicineCategory,
} from '../../../../../model/types';
import {GenerationOptionPanel} from '../GenerationOptionPanel/GenerationOptionPanel';
import styles from './AiDescriptionGenerationOption.module.less';

const nonMedicineCategoryOptions = [
    {description: 'Добавки, витамины, нутрицевтики', label: 'БАД', value: 'dietary_supplement'},
    {description: 'Специализированные продукты питания', label: 'Лечебное питание', value: 'medical_nutrition'},
    {description: 'Приборы, тесты, расходные материалы', label: 'Медизделия', value: 'medical_device'},
    {description: 'Уход, личная гигиена, бытовые товары', label: 'Средства гигиены', value: 'hygiene'},
    {description: 'Косметика и средства ухода', label: 'Косметика', value: 'cosmetics'},
] satisfies Array<{description: string; label: string; value: NonMedicineCategory}>;

const productTypeOptions = [
    {
        description: 'Для препаратов с действующим веществом, формой выпуска и фармакологической информацией.',
        icon: <Pill size={18}/>,
        label: 'Лекарственный препарат',
        value: 'medicine',
    },
    {
        description: 'Для БАД, лечебного питания, медизделий, гигиены и косметики.',
        icon: <PackageCheck size={18}/>,
        label: 'Нелекарственный товар',
        value: 'non_medicine',
    },
] satisfies Array<{
    description: string;
    icon: ReactNode;
    label: string;
    value: AiDescriptionProductType;
}>;

type AiDescriptionGenerationOptionProps = {
    disabled: boolean;
    generationOptions: GenerationOptions;
    onOptionsChange: (options: GenerationOptions) => void;
};

export function AiDescriptionGenerationOption({
                                                  disabled,
                                                  generationOptions,
                                                  onOptionsChange,
                                              }: AiDescriptionGenerationOptionProps) {
    return (
        <GenerationOptionPanel
            caption="Короткое маркетинговое описание товара. Перед запуском выберите тип товара."
            checked={generationOptions.aiDescription}
            disabled={disabled}
            icon={<Sparkles size={18}/>}
            onToggle={(checked) => onOptionsChange({...generationOptions, aiDescription: checked})}
            title="ИИ-описание"
        >
            {generationOptions.aiDescription && (
                <VStack
                    className={styles.aiDescriptionMenu}
                    gap="14"
                    max
                    onClick={stopPanelToggle}
                    onKeyDown={stopPanelToggle}
                >
                    <div className={styles.productTypeGrid}>
                        {productTypeOptions.map((option) => {
                            const active = generationOptions.aiDescriptionProductType === option.value;

                            return (
                                <button
                                    className={`${styles.choiceCard} ${active ? styles.choiceCardActive : ''}`}
                                    disabled={disabled}
                                    key={option.value}
                                    onClick={() => onOptionsChange({
                                        ...generationOptions,
                                        aiDescriptionProductType: option.value,
                                    })}
                                    type="button"
                                >
                                    <span className={styles.choiceIcon}>{option.icon}</span>
                                    <span className={styles.choiceText}>
                                        <strong>{option.label}</strong>
                                        <small>{option.description}</small>
                                    </span>
                                    {active ? <Check className={styles.choiceCheck} size={17}/> : null}
                                </button>
                            );
                        })}
                    </div>

                    {generationOptions.aiDescriptionProductType === 'non_medicine' && (
                        <VStack align="start" gap="8" max>
                            <span className={styles.sectionLabel}>Категория нелекарственного товара</span>
                            <div className={styles.categoryGrid}>
                                {nonMedicineCategoryOptions.map((option) => {
                                    const active = generationOptions.nonMedicineCategory === option.value;

                                    return (
                                        <button
                                            className={`${styles.categoryCard} ${active ? styles.categoryCardActive : ''}`}
                                            disabled={disabled}
                                            key={option.value}
                                            onClick={() => onOptionsChange({
                                                ...generationOptions,
                                                nonMedicineCategory: option.value,
                                            })}
                                            type="button"
                                        >
                                            <strong>{option.label}</strong>
                                            <small>{option.description}</small>
                                        </button>
                                    );
                                })}
                            </div>
                        </VStack>
                    )}
                </VStack>
            )}
        </GenerationOptionPanel>
    );
}

function stopPanelToggle(event: SyntheticEvent) {
    event.stopPropagation();
}
