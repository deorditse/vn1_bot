import type {KeyboardEvent, ReactNode} from 'react';
import {Checkbox, Typography} from 'antd';

import {HStack, VStack} from '@shared/ui';
import styles from './GenerationOptionPanel.module.less';

const {Text} = Typography;

type GenerationOptionPanelProps = {
    caption: string;
    checked: boolean;
    children?: ReactNode;
    disabled: boolean;
    icon: ReactNode;
    title: string;
    onToggle: (checked: boolean) => void;
};

export function GenerationOptionPanel({
                                          caption,
                                          checked,
                                          children,
                                          disabled,
                                          icon,
                                          title,
                                          onToggle,
                                      }: GenerationOptionPanelProps) {
    const toggle = () => {
        if (!disabled) {
            onToggle(!checked);
        }
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
        if (disabled || (event.key !== 'Enter' && event.key !== ' ')) {
            return;
        }

        event.preventDefault();
        onToggle(!checked);
    };

    return (
        <div
            aria-checked={checked}
            aria-disabled={disabled}
            className={`${styles.optionPanel} ${checked ? styles.optionPanelChecked : ''}`}
            onClick={toggle}
            onKeyDown={handleKeyDown}
            role="checkbox"
            tabIndex={disabled ? -1 : 0}
        >
            <VStack gap="12" max>
                <HStack align="start" gap="12" max>
                    <Checkbox
                        className={styles.optionCheckbox}
                        checked={checked}
                        disabled={disabled}
                        onChange={(event) => onToggle(event.target.checked)}
                        onClick={(event) => event.stopPropagation()}
                    />
                    <HStack align="center" className={styles.optionIcon} justify="center">
                        {icon}
                    </HStack>
                    <VStack align="start" gap="4">
                        <Text className={styles.optionTitle}>{title}</Text>
                        <Text className={styles.optionCaption}>{caption}</Text>
                    </VStack>
                </HStack>

                {children}
            </VStack>
        </div>
    );
}
