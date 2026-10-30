export const uploadLibrary = async (file: File): Promise<string> => {
  const csrfResponse = await fetch('/api/books/csrf', {
    credentials: 'same-origin',
    cache: 'no-store',
  });

  if (!csrfResponse.ok) {
    throw new Error('Не удалось получить CSRF-токен. Проверьте доступность сервера.');
  }

  const { csrfToken } = await csrfResponse.json();
  if (typeof csrfToken !== 'string' || !csrfToken) {
    throw new Error('Сервер не вернул CSRF-токен.');
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/books/upload_library', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'X-CSRFToken': csrfToken },
    body: formData,
  });

  if (response.status === 413) {
    throw new Error('Файл слишком большой. Максимальный размер JSON-файла — 10 МиБ.');
  }
  if (response.status === 403) {
    throw new Error('Загрузка отклонена проверкой CSRF. Обновите страницу и повторите попытку.');
  }
  if (response.status >= 500) {
    throw new Error(`Не удалось обработать файл на сервере (HTTP ${response.status}).`);
  }

  const message = await response.text();
  if (!response.ok) {
    throw new Error(message || `Ошибка загрузки: HTTP ${response.status}`);
  }

  return message || 'Файл обработан.';
};
