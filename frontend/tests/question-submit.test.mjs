import assert from 'node:assert/strict';
import { afterEach, mock, test } from 'node:test';
import { handleQuestionSubmit } from '../src/handlers/handleQuestionSubmit.ts';

afterEach(() => mock.restoreAll());

test('reports a network error once and resets the loading state', async () => {
  mock.method(globalThis, 'fetch', async () => { throw new Error('Нет соединения'); });
  const loading = [];
  const errors = [];
  const answers = [];

  await handleQuestionSubmit('Книги', value => loading.push(value), value => answers.push(value), message => errors.push(message));

  assert.deepEqual(errors, ['Нет соединения']);
  assert.deepEqual(loading, [true, false]);
  assert.deepEqual(answers, []);
});

test('successful requests update the answer without emitting an error notification', async () => {
  mock.method(globalThis, 'fetch', async () => new Response('Рекомендация'));
  const errors = [];
  const answers = [];

  await handleQuestionSubmit('Книги', () => {}, value => answers.push(value), message => errors.push(message));

  assert.deepEqual(answers, ['Рекомендация']);
  assert.deepEqual(errors, []);
});

test('HTTP errors are reported to the error callback', async () => {
  mock.method(globalThis, 'fetch', async () => new Response('', { status: 502 }));
  const errors = [];

  await handleQuestionSubmit('Книги', () => {}, () => {}, message => errors.push(message));

  assert.deepEqual(errors, ['Ошибка сервера: 502']);
});
