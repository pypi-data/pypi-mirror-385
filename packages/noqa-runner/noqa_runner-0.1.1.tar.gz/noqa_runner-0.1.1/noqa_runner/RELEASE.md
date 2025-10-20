# Runner Package Release Guide

## Подготовка к релизу

1. **Убедитесь, что все изменения закоммичены**
   ```bash
   git status
   git add .
   git commit -m "Prepare runner v0.1.0"
   git push
   ```

2. **Проверьте, что тесты проходят**
   ```bash
   cd runner
   uv run pytest ../tests/runner/ -v
   ```

3. **Проверьте линтер**
   ```bash
   uv run ruff check .
   uv run black --check .
   ```

## Релиз через GitHub Actions

### Способ 1: Через UI

1. Перейдите на https://github.com/noqa-ai/agent/actions
2. Выберите "Release Runner Package" в левом меню
3. Нажмите "Run workflow" справа
4. Заполните форму:
   - **Version**: `0.1.0` (без префикса v)
   - **Pre-release**: отметьте, если это бета-версия
5. Нажмите "Run workflow"

### Способ 2: Через GitHub CLI

```bash
gh workflow run release-runner.yml \
  -f version=0.1.0 \
  -f prerelease=false
```

## Что происходит при релизе

1. ✅ **Test Job**: Запуск pytest и ruff
2. 📦 **Build Job**: Сборка wheel и sdist
3. 🚀 **Publish Job**: Публикация в GitHub Packages
4. 📝 **Release Job**: Создание GitHub Release

## После релиза

### Проверка релиза

```bash
# Проверить GitHub Release
open https://github.com/noqa-ai/agent/releases

# Скачать артефакты
gh release download runner-v0.1.0
```

### Установка пакета

```bash
# Из GitHub Packages
pip install noqa-runner==0.1.0

# Локально для тестирования
cd runner
uv build
pip install dist/noqa_runner-0.1.0-py3-none-any.whl
```

### Тестирование установленного пакета

```bash
# Проверить версию
python -c "import runner; print(runner.__version__)"

# Запустить CLI
noqa-runner --help
```

## Откат релиза

Если релиз содержит критическую ошибку:

1. **Удалить GitHub Release**
   ```bash
   gh release delete runner-v0.1.0 --yes
   ```

2. **Удалить тег**
   ```bash
   git tag -d runner-v0.1.0
   git push origin :refs/tags/runner-v0.1.0
   ```

3. **Создать hotfix релиз**
   - Исправить баг
   - Увеличить версию (например, 0.1.1)
   - Запустить релиз заново

## Версионирование

Используем [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Несовместимые изменения API
- **MINOR** (0.1.0): Новая функциональность, обратно совместимая
- **PATCH** (0.0.1): Багфиксы, обратно совместимые

### Примеры

- `0.1.0` - Первый рабочий релиз
- `0.2.0` - Добавлена новая команда CLI
- `0.2.1` - Исправлен баг в логировании
- `1.0.0` - Стабильный релиз, готов для продакшена

## Pre-release версии

Для тестовых релизов:

```bash
# Alpha
gh workflow run release-runner.yml -f version=0.1.0-alpha.1 -f prerelease=true

# Beta
gh workflow run release-runner.yml -f version=0.1.0-beta.1 -f prerelease=true

# Release Candidate
gh workflow run release-runner.yml -f version=0.1.0-rc.1 -f prerelease=true
```

## Troubleshooting

### Build failed

```bash
# Локальная проверка сборки
cd runner
uv build
ls -la dist/
```

### Tests failed

```bash
# Запустить тесты локально
cd runner
uv run pytest ../tests/runner/ -v -x  # -x останавливается на первой ошибке
```

### Publishing failed

Проверьте:
- Есть ли права на публикацию в GitHub Packages
- Правильно ли настроен `GITHUB_TOKEN`
- Не существует ли уже такая версия пакета

## Полезные команды

```bash
# Проверить changelog
git log --oneline --since="2 weeks ago" -- runner/

# Создать changelog автоматически
git log --pretty=format:"- %s" --since="v0.0.1" -- runner/ > CHANGELOG.md

# Проверить размер пакета
cd runner
uv build
ls -lh dist/
```

## Checklist перед релизом

- [ ] Все тесты проходят локально
- [ ] Линтер не выдает ошибок
- [ ] README.md обновлен
- [ ] RUNNER_REFACTORING.md содержит все изменения
- [ ] Версия в pyproject.toml корректна (будет обновлена автоматически)
- [ ] Создан git tag для версии
- [ ] Все изменения запушены в GitHub
