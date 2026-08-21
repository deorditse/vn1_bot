import {FileText} from 'lucide-react';

import type {GenerationOptions} from '../../../../../model/types';
import {GenerationOptionPanel} from '../GenerationOptionPanel/GenerationOptionPanel';

type InstructionGenerationOptionProps = {
    disabled: boolean;
    generationOptions: GenerationOptions;
    onOptionsChange: (options: GenerationOptions) => void;
};

export function InstructionGenerationOption({
                                                disabled,
                                                generationOptions,
                                                onOptionsChange,
                                            }: InstructionGenerationOptionProps) {
    return (
        <GenerationOptionPanel
            caption="Готовые HTML-меню и разделы для публикации на сайте"
            checked={generationOptions.instruction}
            disabled={disabled}
            icon={<FileText size={18}/>}
            onToggle={(checked) => onOptionsChange({...generationOptions, instruction: checked})}
            title="HTML-инструкция"
        />
    );
}
