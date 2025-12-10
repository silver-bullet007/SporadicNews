#!/bin/bash
# Quick commands for managing Sporadic News systemd services

case "$1" in
    start)
        echo "Starting Sporadic News services..."
        sudo systemctl start producer.timer
        sudo systemctl start consumer.timer
        echo "✓ Services started"
        ;;
    stop)
        echo "Stopping Sporadic News services..."
        sudo systemctl stop producer.timer
        sudo systemctl stop consumer.timer
        echo "✓ Services stopped"
        ;;
    restart)
        echo "Restarting Sporadic News services..."
        sudo systemctl restart producer.timer
        sudo systemctl restart consumer.timer
        echo "✓ Services restarted"
        ;;
    status)
        echo "=== Producer Timer ==="
        systemctl status producer.timer --no-pager
        echo ""
        echo "=== Consumer Timer ==="
        systemctl status consumer.timer --no-pager
        echo ""
        echo "=== Active Timers ==="
        systemctl list-timers producer.timer consumer.timer --no-pager
        ;;
    logs)
        if [ "$2" == "producer" ]; then
            sudo journalctl -u producer.service -f
        elif [ "$2" == "consumer" ]; then
            sudo journalctl -u consumer.service -f
        else
            echo "Showing recent logs for both services..."
            echo ""
            echo "=== Producer Logs (last 20 lines) ==="
            sudo journalctl -u producer.service -n 20 --no-pager
            echo ""
            echo "=== Consumer Logs (last 20 lines) ==="
            sudo journalctl -u consumer.service -n 20 --no-pager
            echo ""
            echo "To follow logs in real-time:"
            echo "  $0 logs producer"
            echo "  $0 logs consumer"
        fi
        ;;
    enable)
        echo "Enabling Sporadic News services to start on boot..."
        sudo systemctl enable producer.timer
        sudo systemctl enable consumer.timer
        echo "✓ Services enabled"
        ;;
    disable)
        echo "Disabling Sporadic News services from starting on boot..."
        sudo systemctl disable producer.timer
        sudo systemctl disable consumer.timer
        echo "✓ Services disabled"
        ;;
    test-producer)
        echo "Running producer manually (one-shot)..."
        sudo systemctl start producer.service
        echo "Check logs with: $0 logs producer"
        ;;
    test-consumer)
        echo "Running consumer manually (one-shot)..."
        sudo systemctl start consumer.service
        echo "Check logs with: $0 logs consumer"
        ;;
    uninstall)
        echo "Uninstalling Sporadic News services..."
        sudo systemctl stop producer.timer consumer.timer
        sudo systemctl disable producer.timer consumer.timer
        sudo rm /etc/systemd/system/producer.service
        sudo rm /etc/systemd/system/producer.timer
        sudo rm /etc/systemd/system/consumer.service
        sudo rm /etc/systemd/system/consumer.timer
        sudo systemctl daemon-reload
        echo "✓ Services uninstalled"
        ;;
    *)
        echo "Sporadic News - Service Management"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  start          - Start both timers"
        echo "  stop           - Stop both timers"
        echo "  restart        - Restart both timers"
        echo "  status         - Show status of both timers"
        echo "  logs           - Show recent logs from both services"
        echo "  logs producer  - Follow producer logs in real-time"
        echo "  logs consumer  - Follow consumer logs in real-time"
        echo "  enable         - Enable services to start on boot"
        echo "  disable        - Disable services from starting on boot"
        echo "  test-producer  - Run producer once manually"
        echo "  test-consumer  - Run consumer once manually"
        echo "  uninstall      - Remove all systemd files"
        echo ""
        exit 1
        ;;
esac
