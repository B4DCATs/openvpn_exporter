#!/bin/bash

# OpenVPN Exporter - Простой запуск
# Автоматически настраивает и запускает экспортер

set -e

echo "🚀 OpenVPN Exporter - Простой запуск"

# Проверяем права
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите с правами root: sudo ./run.sh"
    exit 1
fi

# Быстрая настройка прав на файл статуса
echo "🔧 Настройка прав доступа..."
if [ -f "/var/log/openvpn/status.log" ]; then
    chmod 644 /var/log/openvpn/status.log 2>/dev/null || true
fi

# Запуск экспортера
echo "🐳 Запуск OpenVPN Exporter..."
docker-compose up -d

echo "✅ Готово! Экспортер запущен на http://localhost:9176"
echo "📊 Метрики: http://localhost:9176/metrics"
echo "🛑 Остановка: docker-compose down"