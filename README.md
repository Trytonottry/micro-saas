# LeadPing SaaS (production-ready MVP)

LeadPing — коммерческий SaaS для малого бизнеса: API и веб-интерфейс для отправки автоматических напоминаний клиентам (например, подтверждение записи, напоминание об оплате, follow-up после услуги).

## 1) Идея сервиса

**Тип:** сервис для малого бизнеса.  
**Проблема:** у салонов, клиник, мастеров и сервисных компаний низкая дисциплина коммуникаций с клиентами.  
**Решение:** единый API + очередь фоновых задач + лимиты и тарифы для массовых, но легковесных уведомлений.

## 2) Почему сервис может приносить деньги

- Понятная бизнес-ценность: меньше no-show, выше повторные продажи.
- Низкий порог интеграции: REST API и простая панель.
- Подписочная модель с ограничениями по количеству событий.
- Низкая инфраструктурная нагрузка, подходит для homelab с ARM-узлами.

## 3) Архитектура системы

- **FastAPI API**: auth, планы, лимиты, задачи, админка.
- **PostgreSQL**: пользователи, тарифы, usage, задачи.
- **Redis + RQ worker**: фоновые jobs.
- **Prometheus metrics**: `/metrics` scraping.
- **Structured logging**: JSON логирование stdout.
- **Rate limiting**: slowapi per-IP.

## 4) Схема сервисов

- `app` — API + web UI + migrations/bootstrap on start.
- `worker` — RQ worker для очереди `notifications`.
- `db` — PostgreSQL 16.
- `redis` — Redis 7.
- `prometheus` — сбор метрик.

## 5) Структура проекта

```text
app/
  core/
  models/
  schemas/
  services/
  routers/
  workers/
  templates/
  static/
alembic/
  versions/
scripts/
.github/workflows/
```

## 6) Быстрый запуск

```bash
cp .env.example .env
docker compose up -d --build
```

Проверка:

- API: `http://<host>:8000/docs`
- Health: `http://<host>:8000/health`
- Metrics: `http://<host>:8000/metrics`
- Prometheus: `http://<host>:9090`

## 7) Деплой в homelab

### Минимальная инфраструктура

- 1x Mini PC (x86_64) — основной node: app, worker, db, redis, prometheus.
- Orange Pi / Mango Pi — резервные node для worker/prometheus (по желанию).

### Распределение по устройствам

- **Mini PC (Ubuntu Server):** API + PostgreSQL + Redis + Prometheus.
- **Orange Pi 3 Zero:** backup worker / cron backup runner.
- **Mango Pi:** secondary worker, canary deployment, smoke checks.
- **NAS:** бэкапы БД, дампы Redis RDB, .env зашифрованный архив.
- **MikroTik:** reverse proxy/NAT/Firewall, allow only 80/443 and VPN admin.

## 8) Инструкция обновления

```bash
git pull
docker compose build app worker
docker compose up -d app worker
docker compose exec app alembic upgrade head
```

## 9) Инструкция backup

### PostgreSQL backup

```bash
docker compose exec db pg_dump -U postgres leadping > backup_$(date +%F).sql
```

### Restore

```bash
cat backup_2026-01-01.sql | docker compose exec -T db psql -U postgres -d leadping
```

Рекомендуется cron + отправка архивов на NAS.

## 10) Мониторинг

- Prometheus scrape `/metrics`.
- Healthcheck контейнеров в compose.
- Рекомендуется добавить Grafana и alertmanager в следующем этапе.

## 11) Безопасность

- JWT auth.
- Bcrypt hashing.
- Rate limit per IP.
- Секреты через `.env`.
- Минимальные открытые порты (8000/9090 только во внутренней сети; наружу через reverse proxy и TLS).

## 12) Масштабирование

- Горизонтально масштабировать `app` и `worker`.
- Вынести PostgreSQL на отдельный host/NAS-backed volume.
- Добавить read-replica PostgreSQL при росте.
- Redis Sentinel/Cluster при необходимости.

## 13) Модель монетизации

- **Starter**: 490 ₽/мес, 200 событий.
- **Growth**: 1490 ₽/мес, 2000 событий.
- **Pro**: 4990 ₽/мес, 20000 событий.
- overage: +0.8 ₽ за событие сверх лимита (можно добавить billing webhook).

## 14) Приём платежей

MVP: ручной биллинг + статус плана в админке.  
Production: интеграция YooKassa/CloudPayments:

1. webhook `payment.succeeded`
2. обновление плана пользователя
3. запись в billing_events таблицу
4. авто-retry при сбое

## 15) Маркетинг и первые клиенты

- Ниша: салоны красоты, стоматологии, небольшие B2C сервисы.
- Каналы: Telegram-чаты локального бизнеса, Avito услуги автоматизации, VK ads на гео.
- Offer: "Уменьшим no-show на 20% за 7 дней".
- First 10 клиентов: ручной онбординг + white-glove setup.

## 16) Оценка нагрузки

На Mini PC 4-core / 8GB RAM:

- 1000 пользователей
- 30k–150k tasks/мес
- peak ~10-20 RPS API при 1-2 воркерах

На старте 5-10k руб/мес достаточно 10-25 платных Starter/Growth пользователей.

## 17) CI/CD пример

GitHub Actions workflow включает lint-like smoke, сборку image и миграции в deploy job.

## 18) Админ доступ по умолчанию

Берётся из `.env`:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

Создаётся при старте `scripts/bootstrap.py`.
