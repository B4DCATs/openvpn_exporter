# OpenVPN Exporter - Простое развертывание

[🇷🇺](DEPLOYMENT.md) (текущая) [🇺🇸](../en/DEPLOYMENT.md)

## Быстрый старт

### 1. Установка OpenVPN
Используйте скрипт для установки OpenVPN:
```bash
wget https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
```

### 2. Настройка OpenVPN для экспорта метрик
Добавьте в конфигурацию OpenVPN сервера (`/etc/openvpn/server.conf`):
```
# Статус файл для мониторинга
status /var/log/openvpn/status.log 10
status-version 2
```

Перезапустите OpenVPN:
```bash
sudo systemctl restart openvpn@server
```

### 3. Запуск OpenVPN Exporter

#### Вариант 1: Docker Compose (рекомендуется)
```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/openvpn_exporter.git
cd openvpn_exporter

# Запустите экспортер
docker compose up -d
```

#### Вариант 2: Docker напрямую
```bash
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/status.log" \
  ghcr.io/b4dcats/openvpn_exporter:latest
```

### 4. Настройка Prometheus
Добавьте в конфигурацию Prometheus (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'openvpn-metrics'
    static_configs:
      - targets: ['YOUR_SERVER_IP:9176']
    scrape_interval: 30s
```

### 5. Настройка Grafana
1. Импортируйте dashboard из файла `dashboard.json.tmp`
2. Настройте Prometheus как источник данных
3. Dashboard будет отображать:
   - Статус OpenVPN сервера
   - Количество подключенных клиентов
   - Трафик по клиентам
   - Топ активных пользователей

## Проверка работы

### Проверка экспортера
```bash
curl http://localhost:9176/metrics
curl http://localhost:9176/health
```

### Проверка метрик в Prometheus
Откройте `http://YOUR_PROMETHEUS_IP:9090` и выполните запрос:
```
openvpn_up
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `LISTEN_ADDRESS` | `:9176` | Адрес для прослушивания |
| `TELEMETRY_PATH` | `/metrics` | Путь для метрик |
| `STATUS_PATHS` | `/var/log/openvpn/status.log` | Пути к файлам статуса OpenVPN |
| `IGNORE_INDIVIDUALS` | `false` | Игнорировать метрики отдельных клиентов |
| `LOG_LEVEL` | `INFO` | Уровень логирования |

## Troubleshooting

### Экспортер не видит файлы статуса
```bash
# Проверьте права доступа
ls -la /var/log/openvpn/status.log

# Проверьте содержимое файла
cat /var/log/openvpn/status.log
```

### Метрики не появляются в Prometheus
1. Проверьте подключение: `curl http://YOUR_SERVER_IP:9176/metrics`
2. Проверьте конфигурацию Prometheus
3. Проверьте логи: `docker logs openvpn-exporter`

### Dashboard не отображает данные
1. Убедитесь, что Prometheus собирает метрики
2. Проверьте временной диапазон в Grafana
3. Убедитесь, что OpenVPN сервер активен и есть подключенные клиенты
