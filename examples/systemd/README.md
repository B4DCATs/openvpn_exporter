# OpenVPN Exporter - Systemd Service Installation

Этот раздел содержит инструкции по установке OpenVPN Exporter как systemd демона (без Docker).

## 📋 Требования

- Linux система с systemd
- Python 3.11 или выше
- pip3 для установки зависимостей
- Доступ к файлам статуса OpenVPN

## 🚀 Быстрая установка

### Автоматическая установка

```bash
# Клонируйте репозиторий
git clone https://github.com/B4DCATs/openvpn_exporter.git
cd openvpn_exporter

# Запустите скрипт установки
sudo ./examples/systemd/install-systemd.sh
```

### Ручная установка

#### 1. Создайте системного пользователя

```bash
sudo useradd -r -s /bin/false -d /opt/openvpn-exporter openvpn-exporter
```

#### 2. Установите зависимости

```bash
pip3 install -r requirements.txt
# или глобально:
sudo pip3 install -r requirements.txt
```

#### 3. Скопируйте файлы

```bash
sudo mkdir -p /opt/openvpn-exporter
sudo cp openvpn_exporter.py /opt/openvpn-exporter/
sudo chmod +x /opt/openvpn-exporter/openvpn_exporter.py
sudo chown -R openvpn-exporter:openvpn-exporter /opt/openvpn-exporter
```

#### 4. Создайте конфигурацию

```bash
sudo mkdir -p /etc/openvpn-exporter
sudo cp examples/systemd/openvpn-exporter.conf /etc/openvpn-exporter/
sudo nano /etc/openvpn-exporter/openvpn-exporter.conf
```

Отредактируйте конфигурацию, указав путь к файлу статуса OpenVPN:

```bash
STATUS_PATHS=/var/log/openvpn/status.log
```

#### 5. Установите systemd service

```bash
sudo cp examples/systemd/openvpn-exporter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openvpn-exporter
sudo systemctl start openvpn-exporter
```

## ⚙️ Конфигурация

Файл конфигурации находится в `/etc/openvpn-exporter/openvpn-exporter.conf`:

```bash
# Адрес для прослушивания
LISTEN_ADDRESS=:9176

# Пути к файлам статуса OpenVPN (через запятую для нескольких)
STATUS_PATHS=/var/log/openvpn/status.log

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Разрешенные IP адреса (через запятую, оставьте пустым для разрешения всех)
ALLOWED_IPS=

# Игнорировать метрики отдельных клиентов
IGNORE_INDIVIDUALS=false
```

### Примеры конфигурации

**Множественные файлы статуса:**
```bash
STATUS_PATHS=/var/log/openvpn/server1.status,/var/log/openvpn/server2.status
```

**Ограничение доступа по IP:**
```bash
ALLOWED_IPS=192.168.1.100,10.0.0.50,monitoring-server.local
```

**Только агрегированные метрики (без метрик отдельных клиентов):**
```bash
IGNORE_INDIVIDUALS=true
```

## 🔧 Управление службой

### Основные команды

```bash
# Запустить службу
sudo systemctl start openvpn-exporter

# Остановить службу
sudo systemctl stop openvpn-exporter

# Перезапустить службу
sudo systemctl restart openvpn-exporter

# Проверить статус
sudo systemctl status openvpn-exporter

# Включить автозапуск при загрузке системы
sudo systemctl enable openvpn-exporter

# Отключить автозапуск
sudo systemctl disable openvpn-exporter
```

### Просмотр логов

```bash
# Последние логи
sudo journalctl -u openvpn-exporter

# Логи в реальном времени
sudo journalctl -u openvpn-exporter -f

# Логи за последний час
sudo journalctl -u openvpn-exporter --since "1 hour ago"

# Логи с определенного времени
sudo journalctl -u openvpn-exporter --since "2025-01-12 10:00:00"
```

### Проверка работы

```bash
# Проверка health endpoint
curl http://localhost:9176/health

# Просмотр метрик
curl http://localhost:9176/metrics

# Проверка доступности
curl -I http://localhost:9176/metrics
```

## 🔄 Обновление

```bash
# Остановите службу
sudo systemctl stop openvpn-exporter

# Обновите файлы
cd /path/to/openvpn_exporter
git pull
sudo cp openvpn_exporter.py /opt/openvpn-exporter/
sudo chown openvpn-exporter:openvpn-exporter /opt/openvpn-exporter/openvpn_exporter.py

# Обновите зависимости (если нужно)
sudo pip3 install -r requirements.txt --upgrade

# Запустите службу
sudo systemctl start openvpn-exporter
```

## 🐛 Устранение неполадок

### Служба не запускается

```bash
# Проверьте статус
sudo systemctl status openvpn-exporter

# Проверьте логи
sudo journalctl -u openvpn-exporter -n 50

# Проверьте конфигурацию
sudo cat /etc/openvpn-exporter/openvpn-exporter.conf

# Проверьте права доступа к файлам
ls -la /opt/openvpn-exporter/
ls -la /var/log/openvpn/status.log
```

### Файл статуса не найден

```bash
# Найдите файлы статуса OpenVPN
find /var/log -name "*openvpn*" -type f
find /etc/openvpn -name "*status*" -type f

# Проверьте конфигурацию OpenVPN
grep -r "status" /etc/openvpn/

# Обновите STATUS_PATHS в конфигурации
sudo nano /etc/openvpn-exporter/openvpn-exporter.conf
sudo systemctl restart openvpn-exporter
```

### Проблемы с правами доступа

```bash
# Проверьте права на файл статуса
ls -la /var/log/openvpn/status.log

# Добавьте пользователя openvpn-exporter в группу, которая имеет доступ
# или измените права на файл статуса
sudo chmod 644 /var/log/openvpn/status.log

# Проверьте права на директорию
ls -ld /var/log/openvpn/
```

### Метрики недоступны

```bash
# Проверьте, что служба запущена
sudo systemctl status openvpn-exporter

# Проверьте, что порт прослушивается
sudo netstat -tlnp | grep 9176
# или
sudo ss -tlnp | grep 9176

# Проверьте firewall
sudo iptables -L -n | grep 9176
# или для firewalld
sudo firewall-cmd --list-ports

# Проверьте ALLOWED_IPS в конфигурации
grep ALLOWED_IPS /etc/openvpn-exporter/openvpn-exporter.conf
```

## 🔒 Безопасность

### Рекомендации

1. **Ограничьте доступ по IP:**
   ```bash
   ALLOWED_IPS=192.168.1.100,10.0.0.50
   ```

2. **Используйте firewall:**
   ```bash
   # iptables
   sudo iptables -A INPUT -p tcp --dport 9176 -s 192.168.1.0/24 -j ACCEPT
   sudo iptables -A INPUT -p tcp --dport 9176 -j DROP
   
   # firewalld
   sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="9176" protocol="tcp" accept'
   sudo firewall-cmd --reload
   ```

3. **Запуск от непривилегированного пользователя:**
   Служба уже настроена на запуск от пользователя `openvpn-exporter` без прав root.

4. **Ограничение доступа к файлам:**
   Systemd service использует `ProtectSystem=strict` и `ReadOnlyPaths` для ограничения доступа.

## 📊 Интеграция с Prometheus

Добавьте в `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'openvpn-exporter'
    static_configs:
      - targets: ['localhost:9176']
    scrape_interval: 30s
    metrics_path: /metrics
```

## 🔄 Сравнение с Docker

| Аспект | Systemd | Docker |
|--------|---------|--------|
| Установка | Требует Python и зависимости | Только Docker |
| Обновление | Обновление файлов и зависимостей | Обновление образа |
| Логи | journalctl | docker logs |
| Конфигурация | Файл в /etc | Переменные окружения |
| Ресурсы | Меньше накладных расходов | Больше накладных расходов |
| Изоляция | Меньше изоляции | Полная изоляция |

Выберите метод установки в зависимости от ваших потребностей:
- **Systemd**: для прямого запуска на хосте, меньше накладных расходов
- **Docker**: для контейнеризации, легче обновление и изоляция

