# 🚀 Queue Manager - Быстрый старт

## Что это?

Queue Manager - это полнофункциональная система управления очередями заданий для Linux с поддержкой multiprocessing, systemd интеграцией и веб-интерфейсом.

## ⚡ Быстрая установка

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/queuemgr.git
cd queuemgr

# Установите сервис (требуются права root)
sudo ./install.sh
```

## 🎯 Основные возможности

- **🚀 Автоматическое управление процессами** - каждое задание выполняется в отдельном процессе
- **📊 Мониторинг в реальном времени** - отслеживание статуса и прогресса заданий
- **🖥️ Множественные интерфейсы** - CLI, веб-интерфейс, systemd сервис
- **⚙️ Systemd интеграция** - автозапуск и управление через systemctl
- **🔧 Обработка ошибок** - автоматическое восстановление и graceful shutdown
- **📈 Масштабируемость** - поддержка множества параллельных заданий

## 🛠️ Типы заданий

- **Обработка данных** - большие датасеты, ETL процессы
- **Файловые операции** - копирование, перемещение, архивирование
- **API вызовы** - интеграция с внешними сервисами
- **Операции с БД** - запросы, обновления, миграции
- **Мониторинг** - сбор метрик, алерты, отчеты

## 📋 Управление сервисом

```bash
# Статус сервиса
sudo systemctl status queuemgr

# Запуск/остановка
sudo systemctl start queuemgr
sudo systemctl stop queuemgr

# Просмотр логов
sudo journalctl -u queuemgr -f
```

## 🖥️ Интерфейсы

### CLI
```bash
# Управление заданиями
/opt/queuemgr/.venv/bin/python -m queuemgr.service.cli job list
/opt/queuemgr/.venv/bin/python -m queuemgr.service.cli job add
/opt/queuemgr/.venv/bin/python -m queuemgr.service.cli monitor
```

### Веб-интерфейс
```bash
# Запуск веб-интерфейса
/opt/queuemgr/.venv/bin/python -m queuemgr.service.web

# Откройте в браузере: http://localhost:5000
```

## 📚 Примеры использования

```python
from queuemgr.proc_api import proc_queue_system
from queuemgr.jobs.base import QueueJobBase

class MyJob(QueueJobBase):
    def execute(self):
        print(f"Выполняю задание {self.job_id}")
        # Ваша логика здесь
        
    def on_start(self):
        print("Задание запущено")
        
    def on_end(self):
        print("Задание завершено")

# Использование
with proc_queue_system() as queue:
    queue.add_job(MyJob, "my-job-1", {"param": "value"})
    queue.start_job("my-job-1")
```

## 📖 Документация

- [Полная документация](SERVICE_README.md)
- [Техническая спецификация](docs/tech_spec.md)
- [Примеры использования](queuemgr/examples/)

## 🎯 Готово к продакшну

- ✅ Все тесты проходят
- ✅ Код отформатирован и проверен
- ✅ Полная документация
- ✅ Примеры использования
- ✅ Systemd интеграция
- ✅ Обработка ошибок

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE

---

**Queue Manager** - надежная система управления очередями заданий для Linux! 🚀
