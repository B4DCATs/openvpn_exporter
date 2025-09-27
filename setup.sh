#!/bin/bash

# OpenVPN Exporter - Автоматическая настройка и запуск
# Этот скрипт настраивает все необходимое для работы экспортера

set -e

echo "🚀 OpenVPN Exporter - Автоматическая настройка"

# Проверяем, что мы root или имеем sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться с правами root или через sudo"
    echo "Использование: sudo ./setup.sh"
    exit 1
fi

echo "📋 Проверка системы..."

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверяем Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Проверяем OpenVPN
if ! systemctl is-active --quiet openvpn@server; then
    echo "⚠️  OpenVPN сервер не запущен. Запускаем..."
    systemctl start openvpn@server
    sleep 2
fi

echo "✅ OpenVPN сервер активен"

# Создаем директории если не существуют
echo "📁 Создание необходимых директорий..."
mkdir -p /var/log/openvpn
mkdir -p /etc/openvpn

# Настраиваем права на файл статуса
echo "🔧 Настройка прав доступа..."

# Проверяем, существует ли файл статуса
if [ -f "/var/log/openvpn/status.log" ]; then
    echo "📄 Файл статуса найден, настраиваем права..."
    chmod 644 /var/log/openvpn/status.log
    chown root:root /var/log/openvpn/status.log
else
    echo "⚠️  Файл статуса не найден, создаем пустой..."
    touch /var/log/openvpn/status.log
    chmod 644 /var/log/openvpn/status.log
    chown root:root /var/log/openvpn/status.log
fi

# Настраиваем OpenVPN для создания файла статуса с правильными правами
echo "⚙️  Настройка OpenVPN..."

# Проверяем конфигурацию OpenVPN
if [ -f "/etc/openvpn/server.conf" ]; then
    # Добавляем настройки статуса если их нет
    if ! grep -q "status /var/log/openvpn/status.log" /etc/openvpn/server.conf; then
        echo "📝 Добавление настроек статуса в OpenVPN..."
        echo "" >> /etc/openvpn/server.conf
        echo "# OpenVPN Exporter settings" >> /etc/openvpn/server.conf
        echo "status /var/log/openvpn/status.log 10" >> /etc/openvpn/server.conf
        echo "status-version 2" >> /etc/openvpn/server.conf
    fi
    
    # Перезапускаем OpenVPN для применения настроек
    echo "🔄 Перезапуск OpenVPN..."
    systemctl restart openvpn@server
    sleep 3
fi

# Проверяем, что файл статуса создался
if [ -f "/var/log/openvpn/status.log" ]; then
    echo "✅ Файл статуса создан и настроен"
    chmod 644 /var/log/openvpn/status.log
else
    echo "⚠️  Файл статуса не создался, но продолжаем..."
fi

# Останавливаем старые контейнеры если есть
echo "🧹 Очистка старых контейнеров..."
docker-compose down 2>/dev/null || true

# Запускаем экспортер
echo "🐳 Запуск OpenVPN Exporter..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ожидание запуска экспортера..."
sleep 5

# Проверяем статус
echo "🔍 Проверка статуса..."

# Проверяем, что контейнер запустился
if docker-compose ps | grep -q "Up"; then
    echo "✅ OpenVPN Exporter успешно запущен!"
    
    # Проверяем доступность метрик
    if curl -s http://localhost:9176/health > /dev/null 2>&1; then
        echo "✅ Метрики доступны по адресу: http://localhost:9176/metrics"
        echo "✅ Health check: http://localhost:9176/health"
    else
        echo "⚠️  Экспортер запущен, но метрики пока недоступны. Подождите несколько секунд."
    fi
    
    echo ""
    echo "🎉 Настройка завершена!"
    echo "📊 Для проверки метрик выполните: curl http://localhost:9176/metrics"
    echo "🛑 Для остановки выполните: docker-compose down"
    
else
    echo "❌ Ошибка запуска экспортера. Проверьте логи:"
    echo "docker-compose logs"
    exit 1
fi
