# Docker Compose Setup

[🇺🇸](DOCKER_COMPOSE.md) (current) [🇷🇺](../ru/DOCKER_COMPOSE.md)

## 🚀 Production (Production)

Использует готовый образ из GitHub Container Registry:

```bash
# Запуск продакшен версии
docker-compose up -d

# Остановка
docker-compose down
```

**Особенности:**
- ✅ Использует `ghcr.io/b4dcats/openvpn_exporter:latest`
- ✅ Стабильная версия
- ✅ Быстрый запуск
- ✅ Логирование: INFO

## 🛠️ Development (Разработка)

Собирает образ локально для разработки:

```bash
# Запуск dev версии
docker-compose -f docker-compose.dev.yml up -d

# Пересборка и запуск
docker-compose -f docker-compose.dev.yml up --build -d

# Остановка
docker-compose -f docker-compose.dev.yml down
```

**Особенности:**
- ✅ Собирает образ локально
- ✅ Монтирует исходный код
- ✅ Логирование: DEBUG
- ✅ Горячая перезагрузка кода

## 📊 Сравнение

| Функция | Production | Development |
|---------|------------|-------------|
| Образ | `ghcr.io/b4dcats/openvpn_exporter:latest` | Локальная сборка |
| Контейнер | `openvpn-exporter` | `openvpn-exporter-dev` |
| Логи | INFO | DEBUG |
| Код | Встроен в образ | Монтируется |
| Скорость запуска | Быстро | Медленно (сборка) |

## 🔧 Переменные окружения

Создайте файл `.env`:

```bash
# Основные настройки
LISTEN_ADDRESS=:9176
TELEMETRY_PATH=/metrics
STATUS_PATHS=/var/log/openvpn/server.status,/var/log/openvpn/client.status
IGNORE_INDIVIDUALS=false
LOG_LEVEL=INFO

# Безопасность
RATE_LIMIT_WINDOW=60
MAX_REQUESTS_PER_WINDOW=100
```

## 🚀 Быстрый старт

### Production:
```bash
docker-compose up -d
curl http://localhost:9176/metrics
```

### Development:
```bash
docker-compose -f docker-compose.dev.yml up --build -d
curl http://localhost:9176/metrics
```
