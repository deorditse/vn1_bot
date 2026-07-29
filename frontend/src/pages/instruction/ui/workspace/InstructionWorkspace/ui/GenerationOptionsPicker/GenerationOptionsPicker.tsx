import type {GenerationOptions} from '../../../../../model/types';
import {AiDescriptionGenerationOption} from '../AiDescriptionGenerationOption/AiDescriptionGenerationOption';
import {InstructionGenerationOption} from '../InstructionGenerationOption/InstructionGenerationOption';
import styles from './GenerationOptionsPicker.module.less';

type GenerationOptionsPickerProps = {
    disabled: boolean;
    instructionDisabled?: boolean;
    generationOptions: GenerationOptions;
    onOptionsChange: (options: GenerationOptions) => void;
};

export function GenerationOptionsPicker({
                                            disabled,
                                            instructionDisabled = false,
                                            generationOptions,
                                            onOptionsChange,
                                        }: GenerationOptionsPickerProps) {
    return (
        <div className={styles.generationGrid}>
            <InstructionGenerationOption
                disabled={disabled || instructionDisabled}
                generationOptions={generationOptions}
                onOptionsChange={onOptionsChange}
            />
            <AiDescriptionGenerationOption
                disabled={disabled}
                generationOptions={generationOptions}
                onOptionsChange={onOptionsChange}
            />
        </div>
    );
}
