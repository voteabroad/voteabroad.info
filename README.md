# voteabroad.info

Статический сайт проекта «Голосуй за рубежом», опубликованный через GitHub Pages из ветки `gh-pages`.

## Что находится в репозитории

- `index.html` — основная страница сайта.
- `results.html` и `results/index.html` — редиректы на блок результатов на главной странице.
- `assets/` — стили, скрипты, шрифты и изображения сайта.
- `files/` — исходные данные экзит-поллов и подготовленная сводка для интерфейса результатов.
- `scripts/generate_results_summary.py` — генератор компактного JSON-файла с агрегированными результатами.

## Результаты экзит-поллов

Сырые данные остаются в CSV:

```sh
files/voter_responses_exit_polls_voteabroad_info_russia_presidential_election_20240317_v3.csv
```

Для быстрой загрузки на клиенте сайт использует предварительно рассчитанный файл:

```sh
files/results-summary-2024.json
```

Если CSV обновился, нужно пересобрать сводку:

```sh
python3 scripts/generate_results_summary.py
```

## Локальный запуск

Из корня репозитория:

```sh
python3 -m http.server 8000
```

После этого открыть:

```text
http://localhost:8000/#past-projects
```

## Публикация

Рабочая ветка для сайта — `gh-pages`. Изменения лучше делать в отдельной ветке, затем открывать pull request в `gh-pages`.

## Preview-деплой в Cloudflare Workers

Production-сайт продолжает публиковаться через GitHub Pages из ветки `gh-pages`. Для предпросмотра используется отдельный Cloudflare Worker `voteabroad-preview` с Workers Static Assets.

GitHub Actions workflow `.github/workflows/cloudflare-workers-preview.yml` запускается вручную или на pull request в `gh-pages`. Он собирает временную папку `.cloudflare/preview/`, исключая `temp/`, `.git`, `.github`, `.DS_Store` и другие служебные файлы, затем выполняет:

```sh
wrangler versions upload --preview-alias <alias>
```

Это создает Cloudflare preview URL и не меняет production-адрес `voteabroad.info`.

Перед первым запуском preview workflow нужно создать Worker `voteabroad-preview` в Cloudflare. Если удобнее сделать это через CLI, можно один раз выполнить `wrangler deploy` из этой ветки; это затронет только отдельный preview Worker, а не GitHub Pages production.

Для работы workflow нужно добавить в GitHub repository secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
