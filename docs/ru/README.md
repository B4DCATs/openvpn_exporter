# OpenVPN Prometheus Exporter v2.0

**Улучшенная Python реализация с расширенными функциями безопасности**

Этот репозиторий предоставляет безопасный экспортер метрик Prometheus для [OpenVPN](https://openvpn.net/). Версия v2.0 - это полная переработка на Python с значительными улучшениями безопасности и расширенной функциональностью.

## 📚 Документация

[🇷🇺](README.md) (текущая) [🇺🇸](../en/README.md)

## 🚀 Новые возможности в v2.0

### Улучшения безопасности
- **Защита от обхода путей**: Предотвращает атаки обхода директорий
- **Валидация и санитизация входных данных**: Все входные данные проверяются и очищаются
- **Ограничение скорости**: Встроенная защита от злоупотреблений
- **Валидация контента**: Обнаруживает и блокирует подозрительный контент
- **Безопасное логирование**: Структурированное логирование с защитой конфиденциальных данных
- **Контейнер без root**: Запускается как непривилегированный пользователь в Docker

### Производительность и надежность
- **Структурированное логирование**: JSON-форматированные логи с корреляционными ID
- **Проверки здоровья**: Встроенные эндпоинты мониторинга здоровья
- **Обработка ошибок**: Комплексная обработка ошибок и восстановление
- **Эффективность памяти**: Оптимизированное использование памяти
- **Многоэтапная сборка Docker**: Меньшие, более безопасные образы контейнеров

## 🚀 Быстрый старт

**Хотите запустить за 30 секунд?** Смотрите [QUICKSTART.md](QUICKSTART.md)

```bash
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter
./run.sh
```

## 📋 Поддерживаемые форматы статуса OpenVPN

Экспортер поддерживает все форматы файлов статуса OpenVPN:
- **Статистика клиента** (формат OpenVPN STATISTICS)
- **Статистика сервера v2** (разделенные запятыми)
- **Статистика сервера v3** (разделенные табуляцией)
- **Список клиентов OpenVPN** (формат OpenVPN CLIENT LIST)

## 🚀 Способы установки

### Systemd Service (Нативная установка)

Для установки как systemd демона (без Docker):

```bash
# Клонируйте репозиторий
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Автоматическая установка
sudo ./examples/systemd/install-systemd.sh

# Настройте конфигурацию
sudo nano /etc/openvpn-exporter/openvpn-exporter.conf

# Запустите службу
sudo systemctl start openvpn-exporter
sudo systemctl enable openvpn-exporter
```

**Подробные инструкции:** [Systemd Installation Guide](../examples/systemd/README.md)

### Docker

#### Предварительно собранный образ (Рекомендуется)

Используйте предварительно собранный образ из GitHub Container Registry:

```bash
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -v /etc/openvpn:/etc/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/status.log" \
  ghcr.io/b4dcats/openvpn_exporter:latest
```

### Docker Compose (Рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Запустить экспортер
docker compose up -d

# Проверить работу
curl http://localhost:9176/metrics
```

### Сборка из исходного кода

```bash
# Клонировать и собрать
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter
docker build -t openvpn-exporter:v2.0 .

# Запустить
docker run -d \
  --name openvpn-exporter \
  -p 9176:9176 \
  -v /var/log/openvpn:/var/log/openvpn:ro \
  -e STATUS_PATHS="/var/log/openvpn/status.log" \
  openvpn-exporter:v2.0
```

Метрики должны быть доступны по адресу http://localhost:9176/metrics.

## 📊 Примеры метрик

### Статистика клиента

Для файлов статуса клиентов экспортер генерирует метрики, которые могут выглядеть так:

```
openvpn_client_auth_read_bytes_total{status_path="..."} 3.08854782e+08
openvpn_client_post_compress_bytes_total{status_path="..."} 4.5446864e+07
openvpn_client_post_decompress_bytes_total{status_path="..."} 2.16965355e+08
openvpn_client_pre_compress_bytes_total{status_path="..."} 4.538819e+07
openvpn_client_pre_decompress_bytes_total{status_path="..."} 1.62596168e+08
openvpn_client_tcp_udp_read_bytes_total{status_path="..."} 2.92806201e+08
openvpn_client_tcp_udp_write_bytes_total{status_path="..."} 1.97558969e+08
openvpn_client_tun_tap_read_bytes_total{status_path="..."} 1.53789941e+08
openvpn_client_tun_tap_write_bytes_total{status_path="..."} 3.08764078e+08
openvpn_status_update_time_seconds{status_path="..."} 1.490092749e+09
openvpn_up{status_path="..."} 1
```

### Статистика сервера

Для файлов статуса сервера (версии 2 и 3) экспортер генерирует метрики, которые могут выглядеть так:

```
openvpn_server_client_received_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 139583
openvpn_server_client_sent_bytes_total{common_name="...",connection_time="...",real_address="...",status_path="...",username="...",virtual_address="..."} 710764
openvpn_server_route_last_reference_time_seconds{common_name="...",real_address="...",status_path="...",virtual_address="..."} 1.493018841e+09
openvpn_status_update_time_seconds{status_path="..."} 1.490089154e+09
openvpn_up{status_path="..."} 1
openvpn_server_connected_clients 1
```

## 🔧 Использование

Использование openvpn_exporter:

```sh
  -openvpn.status_paths string
    	Пути к файлам статуса OpenVPN. (по умолчанию "examples/client.status,examples/server2.status,examples/server3.status")
  -web.listen-address string
    	Адрес для прослушивания веб-интерфейса и телеметрии. (по умолчанию ":9176")
  -web.telemetry-path string
    	Путь для экспорта метрик. (по умолчанию "/metrics")
  -ignore.individuals bool
        Игнорировать метрики для отдельных лиц (по умолчанию false)
```

Пример:

```sh
openvpn_exporter -openvpn.status_paths /etc/openvpn/openvpn-status.log
```

## 📈 Мониторинг с Prometheus и Grafana

### Настройка Prometheus

Добавьте в конфигурацию Prometheus (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'openvpn-metrics'
    static_configs:
      - targets: ['YOUR_SERVER_IP:9176']
    scrape_interval: 30s
```

### Настройка Grafana

1. Импортируйте dashboard из файла `dashboard.json.tmp`
2. Настройте Prometheus как источник данных
3. Dashboard будет отображать:
   - Статус OpenVPN сервера
   - Количество подключенных клиентов
   - Трафик по клиентам
   - Топ активных пользователей

## 🛠️ Разработка

### Требования
- Python 3.11+
- Docker
- Git

### Установка для разработки

```bash
# Клонировать репозиторий
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Установить зависимости
pip install -r requirements.txt

# Запустить в режиме разработки
python openvpn_exporter.py --openvpn.status_paths examples/client.status,examples/server2.status,examples/server3.status
```

## 🤝 Вклад в проект

Мы приветствуем вклад в проект! Пожалуйста, ознакомьтесь с нашими [руководящими принципами](CONTRIBUTING.md) перед отправкой pull request.

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для деталей.

## 💬 Поддержка

- 🐛 [Сообщить об ошибке](https://github.com/B4DCATs/openvpn_exporter/issues)
- 💡 [Запросить функцию](https://github.com/B4DCATs/openvpn_exporter/issues)
- 💬 [Discord сервер](https://discord.gg/VMKdhujjCW)

## 🔗 Полезные ссылки

- [OpenVPN](https://openvpn.net/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Docker](https://www.docker.com/)
