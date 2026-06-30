import { generateInstruction } from '@shared/api/client';

export async function downloadInstruction(file: File) {
  const blob = await generateInstruction(file);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = 'instruction.txt';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
