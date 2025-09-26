# 🚀 Quick Start - OpenVPN Prometheus Exporter v2.0

## Самый простой способ запуска

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter
```

### 2. Запустите одной командой
```bash
./run.sh
```

**Всё!** Экспортер запущен и готов к работе.

## Что происходит автоматически

- ✅ Собирается Docker образ
- ✅ Создаются необходимые директории
- ✅ Запускается контейнер на порту 9176
- ✅ Монтируются файлы OpenVPN статуса
- ✅ Настраивается безопасность

## Проверка работы

```bash
# Метрики
curl http://localhost:9176/metrics

# Здоровье
curl http://localhost:9176/health

# Веб-интерфейс
open http://localhost:9176/
```

## Настройка Prometheus

Добавьте в ваш `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'openvpn-exporter'
    static_configs:
      - targets: ['IP_АДРЕС_СЕРВЕРА:9176']
    scrape_interval: 30s
```

## Переменные окружения

Можете настроить через переменные окружения:

```bash
# Настройка путей к файлам статуса
export STATUS_PATHS="/var/log/openvpn/server.status,/var/log/openvpn/client.status"

# Настройка порта
export LISTEN_ADDRESS=":9176"

# Настройка логирования
export LOG_LEVEL="INFO"

# Игнорировать индивидуальные метрики (приватность)
export IGNORE_INDIVIDUALS="true"
```

## Docker Compose

Или используйте docker-compose:

```bash
# Создайте .env файл
cp env.example .env

# Отредактируйте .env под ваши нужды
nano .env

# Запустите
docker-compose up -d
```

## Остановка

```bash
# Остановить контейнер
docker stop openvpn-exporter

# Удалить контейнер
docker rm openvpn-exporter
```

## Логи

```bash
# Посмотреть логи
docker logs openvpn-exporter

# Следить за логами в реальном времени
docker logs -f openvpn-exporter
```

## Требования к OpenVPN

Убедитесь, что в конфигурации OpenVPN включен статус:

```bash
# В /etc/openvpn/server.conf
status /var/log/openvpn/server.status
status-version 2
status-update 10
```

## Готово! 🎉

Теперь у вас есть:
- ✅ Безопасный экспортер метрик
- ✅ Защита от атак
- ✅ Rate limiting
- ✅ Структурированные логи
- ✅ Health checks
- ✅ Готовые метрики для Prometheus
