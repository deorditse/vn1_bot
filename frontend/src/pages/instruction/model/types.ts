export type InstructionBlock = {
  key: string;
  title: string;
  content: string;
};

export type CopyTextHandler = (key: string, content: string) => Promise<void>;
