import {Suspense} from 'react';
import {Page} from '@widgets/Page';
import {useInstructionGenerator} from '../../model/useInstructionGenerator';
import {InstructionMarkupResults, InstructionMarkupResultsSkeleton, InstructionResultsSkeleton} from '../results';
import {InstructionAiSummary, InstructionAiSummarySkeleton} from '../summary';
import {InstructionWorkspace} from '../workspace';

const InstructionPage = () => {
    const {
        aiDescription,
        copiedBlock,
        error,
        file,
        generationOptions,
        instruction,
        isAiDescriptionLoading,
        isFileUploading,
        isInstructionLoading,
        isLoading,
        markupBlocks,
        convert,
        copyText,
        generateDescriptionOnly,
        removeSelectedFile,
        resetInstruction,
        selectFile,
        updateGenerationOptions,
    } = useInstructionGenerator();

    const hasResults = Boolean(instruction || aiDescription);
    const isInstructionSkeletonVisible = !instruction && generationOptions.instruction && (isFileUploading || isInstructionLoading);
    const isAiDescriptionSkeletonVisible = !aiDescription && (isAiDescriptionLoading || (generationOptions.aiDescription && isFileUploading));
    const isAiDescriptionBlockVisible = Boolean(instruction || aiDescription || isAiDescriptionSkeletonVisible);
    const isResultsVisible = hasResults || isInstructionSkeletonVisible || isAiDescriptionSkeletonVisible;

    return (
        <Page>
            <InstructionWorkspace
                error={error}
                file={file}
                generationOptions={generationOptions}
                instructionReady={hasResults}
                isLoading={isLoading}
                onConvert={convert}
                onOptionsChange={updateGenerationOptions}
                onRemoveFile={removeSelectedFile}
                onReset={resetInstruction}
                onSelectFile={selectFile}
            />

            {isResultsVisible && (
                <Suspense fallback={<InstructionResultsSkeleton/>}>
                    {isInstructionSkeletonVisible && <InstructionMarkupResultsSkeleton />}
                    {instruction && (
                        <InstructionMarkupResults blocks={markupBlocks} copiedBlock={copiedBlock} onCopy={copyText}/>
                    )}
                    {isAiDescriptionSkeletonVisible ? (
                        <InstructionAiSummarySkeleton />
                    ) : (
                        isAiDescriptionBlockVisible && (
                            <InstructionAiSummary
                                copied={copiedBlock === 'ai_description'}
                                description={aiDescription}
                                isLoading={isAiDescriptionLoading}
                                onGenerate={generateDescriptionOnly}
                                onCopy={copyText}
                            />
                        )
                    )}
                </Suspense>
            )}
        </Page>
    );
};

export default InstructionPage;
