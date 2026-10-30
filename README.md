## Первый запуск


1. Скопируйте `.env.example` в `.env`

   Заполните `LLM_API_KEY` своим ключом провайдера (https://dashboard.iaas.store/services/ai/). Проверьте `LLM_MODEL`
   и `LLM_BASE_URL`. Секретный `.env` не передавайте другим пользователям.

2. Соберите и запустите приложение:
   
   ```powershell
   docker compose up -d --build
   ```

   Одноразовый сервис `init` ждёт Qdrant и Ollama, скачивает выбранную
   embedding-модель, создаёт коллекцию и выполняет миграции Django.
   Если модель уже скачана, повторной загрузки нет. Существующая коллекция
   сохраняется; несовместимая размерность останавливает запуск без удаления данных.
   Django ждёт успешного завершения `init`, nginx — готовности Django.
   Первая сборка backend может
   занять значительное время: зависимости включают sentence-transformers/PyTorch.

3. Откройте **http://localhost/**. Нажмите сову и выберите `task/books.json`
   либо загрузите каталог командой:

   ```powershell
   docker compose exec django python manage.py enrich_book_collection
   ```

   Дополнительный файл из каталога проекта (предварительно этот файт туда нужно положить):

   ```powershell
   docker compose exec django python manage.py enrich_book_collection --file task/other_books.json
   ```

   Повторный импорт обновляет записи с теми же UUID5; другие книги сохраняются.
   Запрос рекомендаций использует платный внешний LLM API.

## Работа через nginx

- `/` — собранный frontend.
- `/api/…` — проксирование в Django с удалением префикса `/api`.
- `/healthz` — проверка nginx.
- `/api/books/csrf` — получение CSRF-токена и cookie перед загрузкой файла.
- Файлы до 10 МиБ проверяет Django; nginx допускает 11 МиБ для multipart-запроса
  вместе с его служебными полями. Более крупный запрос получает HTTP 413.

Изменив frontend или конфигурацию nginx, пересоберите образ:

```powershell
docker compose up -d --build nginx
```

Если порт 80 занят, задайте `APP_PORT=8080` в `.env`, выполните
`docker compose up -d` и откройте http://localhost:8080/.
nginx сохраняет Host вместе с портом, поэтому CSRF работает и на другом порту.

Для доступа с другого устройства в локальной сети установите
`APP_BIND_ADDRESS=0.0.0.0`, добавьте IP/имя компьютера в `DJANGO_ALLOWED_HOSTS`
(сохранив localhost и 127.0.0.1 для healthcheck) и разрешите порт в firewall.
Это конфигурация HTTP для локального запуска; публичный сервер требует HTTPS
и отдельной настройки сервера Django вместо `runserver`.

## Данные и перенос

- Каталог Qdrant сохраняется в `qdrant_data/` рядом с проектом.
- Модели Ollama сохраняются в Docker volume `ollama_data`.
- SQLite остаётся в `db.sqlite3`; исходники backend пока подключены через bind mount
  для продолжения разработки.
- На новом компьютере можно создать пустую коллекцию и повторно загрузить JSON.
  Чтобы перенести весь существующий каталог, сохраните исходные JSON либо используйте
  snapshot Qdrant; `task/books.json` не содержит книг из других загруженных файлов.
- `docker compose down` останавливает приложение. Не используйте `down -v`, если
  хотите сохранить скачанные модели Ollama.

## Проверки

```powershell
docker compose ps
docker compose ps -a init
docker compose exec nginx nginx -t
docker compose exec django python manage.py check
docker compose exec django python manage.py test books
docker compose logs --tail 50 django nginx
```

Backend-тесты подменяют импорт и не записывают книги в Qdrant.
Frontend-тесты доступны при установленном Node.js: `cd frontend`, затем
`npm ci`, `npm test`, `npm run lint`, `npm run build`.

Для разработки frontend по-прежнему можно запускать `npm run dev` в `frontend`.
Proxy Vite отправляет `/api/…` в Django на порту 8000.
