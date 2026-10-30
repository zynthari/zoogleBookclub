import {FloatButton, Spin} from 'antd';
import {useRef} from 'react';
import owl from '../assets/owl.png'

type UploadButtonProps = {
    className?: string;
    uploading: boolean;
    onFileSelected: (file: File) => Promise<void>;
};

export const UploadButton = ({className, uploading, onFileSelected}: UploadButtonProps) => {
    const inputRef = useRef<HTMLInputElement>(null);

    return (
        <>
            <FloatButton
                 icon={uploading ? <Spin size="small" /> : <img src={owl} alt="" width={24} height={24} />}
                 className={className}
                 aria-label="Загрузить каталог книг"
                 tooltip={uploading ? "Каталог загружается…" : "Загрузить JSON с книгами"}
                 disabled={uploading}
                 onClick={() => inputRef.current?.click()}
            />
            <input
              ref={inputRef}
              type="file"
              accept=".json"
              hidden
              disabled={uploading}
              onChange={async (event) => {
                  const input = event.currentTarget;
                  const file = input.files?.[0];
                  if (!file) return;

                  try {
                      await onFileSelected(file);
                  } finally {
                      // Позволяет повторно выбрать тот же файл после импорта или ошибки.
                      input.value = '';
                  }
              }}
            />
        </>
    )
}
