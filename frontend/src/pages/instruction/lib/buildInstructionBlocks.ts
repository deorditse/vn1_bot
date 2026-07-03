import type {GenerateInstructionResponse} from '../api/types';
import type {InstructionBlock} from '../model/types';

export function buildInstructionBlocks(instruction: GenerateInstructionResponse | null): InstructionBlock[] {
  if (!instruction) {
    return [];
  }

  return [
    {
      key: 'html_menu',
      title: 'HTML-меню',
      content: instruction.html_menu,
    },
    {
      key: 'html_content',
      title: 'HTML-контент',
      content: instruction.html_content,
    },
  ];
}
