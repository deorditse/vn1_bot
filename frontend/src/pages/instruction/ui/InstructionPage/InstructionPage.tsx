import {Suspense} from 'react';
import {Page} from '@widgets/Page';
import {useInstructionGenerator} from '../../model/useInstructionGenerator';
import {InstructionMarkupResults, InstructionResultsSkeleton} from '../results';
import {InstructionAiSummary} from '../summary';
import {InstructionWorkspace} from '../workspace';

const InstructionPage = () => {
    const {
        copiedBlock,
        error,
        file,
        instruction,
        isLoading,
        markupBlocks,
        convert,
        copyText,
        removeSelectedFile,
        resetInstruction,
        selectFile,
    } = useInstructionGenerator();

    return (
        <Page>
            <InstructionWorkspace
                error={error}
                file={file}
                instructionReady={Boolean(instruction)}
                isLoading={isLoading}
                onConvert={convert}
                onRemoveFile={removeSelectedFile}
                onReset={resetInstruction}
                onSelectFile={selectFile}
            />

            {instruction && (
                <Suspense fallback={<InstructionResultsSkeleton/>}>
                    <InstructionAiSummary
                        copied={copiedBlock === 'ai_description'}
                        description={instruction.ai_description}
                        onCopy={copyText}
                    />
                    <InstructionMarkupResults blocks={markupBlocks} copiedBlock={copiedBlock} onCopy={copyText}/>
                </Suspense>
            )}
        </Page>
    );
};

export default InstructionPage;
