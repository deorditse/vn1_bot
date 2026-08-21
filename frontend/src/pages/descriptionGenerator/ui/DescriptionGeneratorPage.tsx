import {Alert, Button, Input, Segmented, Typography, Upload} from 'antd';
import type {UploadProps} from 'antd';
import {Download, FileCheck2, FileSpreadsheet, Keyboard, Sparkles, Square, UploadCloud} from 'lucide-react';
import {useMemo, useRef, useState} from 'react';

import dancingCat from '@shared/assets/dancing-cat.gif';
import {Page} from '@widgets/Page';
import {AnimatedLoader, Card, HStack, TablePreview, VStack} from '@shared/ui';
import {useGenerateDescriptionMutation} from '../api/descriptionGeneratorApi';
import type {GenerateDescriptionReport} from '../api/types';
import styles from './DescriptionGeneratorPage.module.less';

const {Text} = Typography;
const {TextArea} = Input;
type InputMode = 'file' | 'form';
type AbortableRequest = {abort: () => void};
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const MAX_RAW_DESCRIPTION_CHARS = 100_000;

function errorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const data = error.data;
    if (typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string') {
      return data.detail;
    }
    if (typeof data === 'object' && data !== null && 'error' in data) {
      const payload = data.error;
      if (typeof payload === 'object' && payload !== null && 'message' in payload && typeof payload.message === 'string') {
        return payload.message;
      }
    }
  }
  return 'Не удалось сформировать таблицу. Попробуйте еще раз.';
}

function downloadWorkbook(blob: Blob) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'generated-descriptions.xlsx';
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

const DescriptionGeneratorPage = () => {
  const [mode, setMode] = useState<InputMode>('file');
  const [file, setFile] = useState<File | null>(null);
  const [itemId, setItemId] = useState('');
  const [rawDescription, setRawDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const [lastResult, setLastResult] = useState<Blob | null>(null);
  const [report, setReport] = useState<GenerateDescriptionReport | null>(null);
  const [generateDescription, {isLoading}] = useGenerateDescriptionMutation();
  const activeRequestRef = useRef<AbortableRequest | null>(null);
  const cancelRequestedRef = useRef(false);

  const uploadProps = useMemo<UploadProps>(() => ({
    accept: '.xls,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    beforeUpload: (nextFile) => {
      const extension = nextFile.name.toLowerCase();
      if (!extension.endsWith('.xls') && !extension.endsWith('.xlsx')) {
        setError('Поддерживаются только файлы XLS и XLSX');
        return Upload.LIST_IGNORE;
      }
      if (nextFile.size > MAX_FILE_BYTES) {
        setError('Размер файла не должен превышать 10 МБ');
        return Upload.LIST_IGNORE;
      }
      setFile(nextFile);
      setError(null);
      setCompleted(false);
      setLastResult(null);
      setReport(null);
      return false;
    },
    fileList: file ? [{uid: file.name, name: file.name, status: 'done'}] : [],
    maxCount: 1,
    onRemove: () => {
      setFile(null);
      setCompleted(false);
      setLastResult(null);
      setReport(null);
    },
    showUploadList: false,
  }), [file]);

  const canSubmit = mode === 'file'
    ? Boolean(file)
    : Boolean(itemId.trim() && rawDescription.trim());

  const submit = async () => {
    if (!canSubmit) {
      setError(mode === 'file' ? 'Выберите XLS/XLSX-файл' : 'Заполните id и сырой текст описания');
      return;
    }

    setError(null);
    setCompleted(false);
    setReport(null);
    cancelRequestedRef.current = false;
    const request = generateDescription(
      mode === 'file'
        ? {mode, file: file as File}
        : {mode, id: itemId.trim(), rawDescription},
    );
    activeRequestRef.current = request;
    try {
      const result = await request.unwrap();
      downloadWorkbook(result.blob);
      setLastResult(result.blob);
      setReport(result.report);
      setCompleted(true);
    } catch (requestError) {
      setError(cancelRequestedRef.current ? 'Генерация остановлена' : errorMessage(requestError));
    } finally {
      activeRequestRef.current = null;
    }
  };

  const cancelGeneration = () => {
    cancelRequestedRef.current = true;
    activeRequestRef.current?.abort();
  };

  const selectMode = (value: InputMode) => {
    setMode(value);
    setError(null);
    setCompleted(false);
    setLastResult(null);
    setReport(null);
  };

  return (
    <Page className={styles.page}>
      <Card className={styles.workspace} padding="24">
        <VStack gap="18" max>
        <div className={styles.workflowIntro}>
          <div className={styles.workflowStep}>
            <span>1</span>
            <div><strong>Добавьте данные</strong><small>Таблица или одна позиция</small></div>
          </div>
          <div className={styles.workflowStep}>
            <span>2</span>
            <div><strong>Запустите обработку</strong><small>Сервис заполнит карточки</small></div>
          </div>
          <div className={styles.workflowStep}>
            <span>3</span>
            <div><strong>Скачайте результат</strong><small>Готовый файл XLSX</small></div>
          </div>
        </div>

        <div className={styles.sourceHeader}>
          <div>
            <Text strong>Исходные данные</Text>
            <Text>Для нескольких товаров используйте таблицу, для одного — ручной ввод.</Text>
          </div>
          <Segmented
            className={styles.modeSwitch}
            disabled={isLoading}
            onChange={(value) => selectMode(value as InputMode)}
            options={[
              {label: 'Таблица', value: 'file', icon: <FileSpreadsheet size={16}/>},
              {label: 'Одна позиция', value: 'form', icon: <Keyboard size={16}/>},
            ]}
            value={mode}
          />
        </div>

        {mode === 'file' ? (
          <Upload.Dragger
            className={`${styles.dropzone} ${file ? styles.dropzoneSelected : ''}`}
            disabled={isLoading}
            {...uploadProps}
          >
            {file ? (
              <div className={styles.fileState}>
                <div className={styles.fileIcon}><FileCheck2 size={24}/></div>
                <div>
                  <strong>{file.name}</strong>
                  <Text>Файл выбран. Можно запускать обработку.</Text>
                </div>
              </div>
            ) : (
              <div className={styles.fileState}>
                <div className={styles.fileIcon}><UploadCloud size={24}/></div>
                <div>
                  <strong>Добавьте таблицу</strong>
                  <Text>Перетащите XLS/XLSX сюда или нажмите для выбора.</Text>
                </div>
              </div>
            )}
          </Upload.Dragger>
        ) : null}

        <TablePreview
          caption="Так должна выглядеть исходная таблица"
          columns={['id', 'разметка сырая']}
          editable={mode === 'form'}
          note="XLS/XLSX · до 100 строк · до 10 МБ"
          rows={mode === 'file' ? [
            ['72128', 'a:2:{s:11:"instruction";a:17:{s:16:"Описание";s:163:"Антикоагулянт прямого действия - селективный ингибитор фактора свертывания крови Ха (FXa).";s:45:"Способ применения и дозы";s:14783:"<p> ...'],
          ] : [[
            <Input
              disabled={isLoading}
              key="id"
              maxLength={128}
              onChange={(event) => {
                setItemId(event.target.value);
                setCompleted(false);
                setLastResult(null);
                setReport(null);
              }}
              placeholder="72128"
              value={itemId}
            />,
            <TextArea
              autoSize={{minRows: 5, maxRows: 16}}
              disabled={isLoading}
              key="raw-description"
              maxLength={MAX_RAW_DESCRIPTION_CHARS}
              onChange={(event) => {
                setRawDescription(event.target.value);
                setCompleted(false);
                setLastResult(null);
                setReport(null);
              }}
              placeholder={'a:2:{s:11:"instruction"; ... }'}
              value={rawDescription}
            />,
          ]]}
        />

        <div className={styles.feedback}>
          {completed && (
            <Alert
              action={lastResult ? (
                <Button icon={<Download size={16}/>} onClick={() => downloadWorkbook(lastResult)} size="small">
                  Скачать ещё раз
                </Button>
              ) : undefined}
              description={(
                <VStack gap="4">
                  <Text>Файл generated-descriptions.xlsx сохранён в загрузки браузера.</Text>
                  {report ? (
                    <Text strong>
                      Строк с ошибкой: {report.errorRows} / Всего строк: {report.totalRows}
                    </Text>
                  ) : null}
                </VStack>
              )}
              message={report?.errorRows ? 'Таблица готова с ошибками' : 'Таблица готова'}
              showIcon
              type={report?.errorRows ? 'warning' : 'success'}
            />
          )}
          {error && <Alert message={error} showIcon type="error"/>}
        </div>

        {!completed ? (
          <HStack justify="end" max>
            <Button
              disabled={!canSubmit}
              icon={<Sparkles size={18}/>}
              loading={isLoading}
              onClick={submit}
              size="large"
              type="primary"
            >
              Сформировать XLSX
            </Button>
          </HStack>
        ) : null}
        </VStack>
      </Card>
      {isLoading ? (
        <AnimatedLoader
          action={(
            <Button danger icon={<Square size={15}/>} onClick={cancelGeneration}>
              Остановить
            </Button>
          )}
          alt="Танцующий белый кот"
          description="Обрабатываем строки и собираем XLSX"
          imageSrc={dancingCat}
          placement="bottom"
          title="Идет генерация таблицы..."
        />
      ) : null}
    </Page>
  );
};

export default DescriptionGeneratorPage;
