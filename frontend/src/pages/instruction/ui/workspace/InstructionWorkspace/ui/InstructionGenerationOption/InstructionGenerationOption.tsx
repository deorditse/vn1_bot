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
            caption="HTML-меню и контент инструкции"
            checked={generationOptions.instruction}
            disabled={disabled}
            icon={<FileText size={18}/>}
            onToggle={(checked) => onOptionsChange({...generationOptions, instruction: checked})}
            title="Генерация инструкции"
        />
    );
}
