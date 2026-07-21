import {Radio} from 'antd';
import {PackageCheck, Pill, Sparkles} from 'lucide-react';

import {HStack, VStack} from '@shared/ui';
import type {GenerationOptions} from '../../../../../model/types';
import {GenerationOptionPanel} from '../GenerationOptionPanel/GenerationOptionPanel';
import styles from './AiDescriptionGenerationOption.module.less';

const nonMedicineCategoryOptions = [
    {label: 'БАД', value: 'dietary_supplement'},
    {label: 'Лечебное питание', value: 'medical_nutrition'},
    {label: 'Медизделия', value: 'medical_device'},
    {label: 'Средства гигиены', value: 'hygiene'},
    {label: 'Косметика', value: 'cosmetics'},
];

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
            caption="Для лекарственных и нелекарственных препаратов"
            checked={generationOptions.aiDescription}
            disabled={disabled}
            icon={<Sparkles size={18}/>}
            onToggle={(checked) => onOptionsChange({...generationOptions, aiDescription: checked})}
            title="ИИ-описания"
        >
            {generationOptions.aiDescription && (
                <VStack
                    className={styles.aiDescriptionMenu}
                    gap="10"
                    max
                    onClick={(event) => event.stopPropagation()}
                    onKeyDown={(event) => event.stopPropagation()}
                >
                    <Radio.Group
                        buttonStyle="solid"
                        disabled={disabled}
                        onChange={(event) => onOptionsChange({
                            ...generationOptions,
                            aiDescriptionProductType: event.target.value
                        })}
                        optionType="button"
                        value={generationOptions.aiDescriptionProductType}
                    >
                        <Radio.Button value="medicine">
                            <HStack align="center" gap="6">
                                <Pill size={15}/>
                                Лекарственные препараты
                            </HStack>
                        </Radio.Button>
                        <Radio.Button value="non_medicine">
                            <HStack align="center" gap="6">
                                <PackageCheck size={15}/>
                                Нелекарственные препараты
                            </HStack>
                        </Radio.Button>
                    </Radio.Group>

                    {generationOptions.aiDescriptionProductType === 'non_medicine' && (
                        <Radio.Group
                            className={styles.categoryGroup}
                            disabled={disabled}
                            onChange={(event) => onOptionsChange({
                                ...generationOptions,
                                nonMedicineCategory: event.target.value
                            })}
                            optionType="button"
                            options={nonMedicineCategoryOptions}
                            value={generationOptions.nonMedicineCategory}
                        />
                    )}
                </VStack>
            )}
        </GenerationOptionPanel>
    );
}
