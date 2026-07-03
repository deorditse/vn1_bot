import {Suspense} from 'react';

import {DynamicModuleLoader} from '@shared/lib/components/DynamicModuleLoader';
import {Page} from '@widgets/Page';
import {instructionApi} from '../../api/instructionApi';
import {useInstructionGenerator} from '../../model/useInstructionGenerator';
import {InstructionMarkupResults, InstructionResultsSkeleton} from '../results';
import {InstructionAiSummary} from '../summary';
import {InstructionWorkspace} from '../workspace';

const reducers = {[instructionApi.reducerPath]: instructionApi.reducer};

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
    <DynamicModuleLoader reducers={reducers}>
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
          <Suspense fallback={<InstructionResultsSkeleton />}>
            <InstructionMarkupResults blocks={markupBlocks} copiedBlock={copiedBlock} onCopy={copyText} />
            <InstructionAiSummary
              copied={copiedBlock === 'ai_description'}
              description={instruction.ai_description}
              onCopy={copyText}
            />
          </Suspense>
        )}
      </Page>
    </DynamicModuleLoader>
  );
};

export default InstructionPage;
