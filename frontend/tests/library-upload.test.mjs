import assert from 'node:assert/strict';
import { afterEach, mock, test } from 'node:test';
import { uploadLibrary } from '../src/handlers/handleLibraryUpload.ts';

afterEach(() => mock.restoreAll());

test('sends the selected file with a CSRF token and returns the server message', async () => {
  const file = new File(['{"books": []}'], 'books.json', { type: 'application/json' });
  const calls = [];
  mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options });
    return calls.length === 1
      ? Response.json({ csrfToken: 'test-token' })
      : new Response('Обработано 2 книги');
  });

  assert.equal(await uploadLibrary(file), 'Обработано 2 книги');
  assert.equal(calls[0].url, '/api/books/csrf');
  assert.equal(calls[1].url, '/api/books/upload_library');
  assert.equal(calls[1].options.method, 'POST');
  assert.equal(calls[1].options.headers['X-CSRFToken'], 'test-token');
  assert.equal(calls[1].options.headers['Content-Type'], undefined);
  assert.ok(calls[1].options.body instanceof FormData);
  assert.equal(calls[1].options.body.get('file').name, 'books.json');
  assert.equal(await calls[1].options.body.get('file').text(), await file.text());
});

test('does not upload when CSRF initialization fails', async () => {
  const fetchMock = mock.method(globalThis, 'fetch', async () => new Response('', { status: 503 }));
  await assert.rejects(uploadLibrary(new File(['{}'], 'books.json')), /CSRF/);
  assert.equal(fetchMock.mock.callCount(), 1);
});

test('rejects a missing CSRF token before uploading', async () => {
  const fetchMock = mock.method(globalThis, 'fetch', async () => Response.json({}));
  await assert.rejects(uploadLibrary(new File(['{}'], 'books.json')), /CSRF/);
  assert.equal(fetchMock.mock.callCount(), 1);
});

test('shows a validation error returned by the backend', async () => {
  let call = 0;
  mock.method(globalThis, 'fetch', async () => ++call === 1
    ? Response.json({ csrfToken: 'test-token' })
    : new Response('Файл слишком большой!', { status: 400 }));
  await assert.rejects(uploadLibrary(new File(['{}'], 'books.json')), /Файл слишком большой/);
});

test('does not expose an HTML CSRF failure page as the error message', async () => {
  let call = 0;
  mock.method(globalThis, 'fetch', async () => ++call === 1
    ? Response.json({ csrfToken: 'test-token' })
    : new Response('<html>Forbidden</html>', { status: 403 }));
  await assert.rejects(uploadLibrary(new File(['{}'], 'books.json')), /CSRF/);
});

test('explains the nginx request size limit without exposing its HTML page', async () => {
  let call = 0;
  mock.method(globalThis, 'fetch', async () => ++call === 1
    ? Response.json({ csrfToken: 'test-token' })
    : new Response('<html>413 Request Entity Too Large</html>', { status: 413 }));
  await assert.rejects(uploadLibrary(new File(['{}'], 'books.json')), /10 МиБ/);
});
