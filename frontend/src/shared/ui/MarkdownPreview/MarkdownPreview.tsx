import ReactMarkdown from 'react-markdown';

import styles from './MarkdownPreview.module.less';

type MarkdownPreviewProps = {
  markdown: string;
};

export function MarkdownPreview({markdown}: MarkdownPreviewProps) {
  return (
    <div className={styles.markdownPreview}>
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}
