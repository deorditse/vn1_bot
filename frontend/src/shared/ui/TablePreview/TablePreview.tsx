import type {ReactNode} from 'react';

import {classNames} from '@shared/lib/classNames';
import styles from './TablePreview.module.less';

type TablePreviewProps = {
  caption: string;
  columns: string[];
  editable?: boolean;
  note?: ReactNode;
  rows: Array<Array<ReactNode>>;
};

export function TablePreview({caption, columns, editable = false, note, rows}: TablePreviewProps) {
  return (
    <figure className={classNames(styles.preview, {[styles.editable]: editable})}>
      <figcaption>
        <strong>{caption}</strong>
        {note ? <span>{note}</span> : null}
      </figcaption>
      <div className={styles.tableFrame}>
        <table>
          <thead>
            <tr>
              {columns.map((column) => <th key={column}>{column}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`}>
                {row.map((cell, cellIndex) => <td key={`cell-${rowIndex}-${cellIndex}`}>{cell}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </figure>
  );
}
