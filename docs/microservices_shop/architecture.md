# Архитектура Microservices Shop

Microservices Shop — учебный backend интернет-магазина. Пользователь регистрируется, просматривает каталог и создаёт заказ. Payment Service автоматически имитирует оплату. Сервис ждёт три секунды и сохраняет успешный результат. В проекте нет интеграции с платёжным провайдером.

## Компоненты и их данные

| Компонент | Ответственность и данные |
|---|---|
| Nginx | Принимает запросы к `/api/` на порту 80 и направляет их в API Gateway. |
| [API Gateway](api-gateway.md) | Предоставляет внешний API, проверяет JWT и доступ к заказу. У gateway нет собственной модели хранения данных магазина. |
| [Auth Service](auth-service.md) | Хранит пользователей в таблице `users`, проверяет пароли и выдаёт JWT. |
| [Catalog Service](catalog-service.md) | Хранит товары в таблице `products` и отдаёт их по HTTP. |
| [Order Service](order-service.md) | Хранит заказы в `orders` и позиции в `order_items`, рассчитывает стоимость и обрабатывает подтверждение оплаты. |
| [Payment Service](payment-service.md) | Хранит платежи в `payments`, имитирует оплату и публикует событие завершения. |
| [RabbitMQ](rabbitmq-events.md) | Передаёт событие завершения оплаты из Payment Service в Order Service. |

Сервисы на FastAPI обмениваются запросами по HTTP. Для хранения данных проект использует PostgreSQL и асинхронный SQLAlchemy. При старте сервисы с БД создают отсутствующие таблицы через `create_all`. Order Service при старте подписывается на очередь, Payment Service подключается к RabbitMQ для публикации.

## Как проходит покупка

```text
Клиент → Nginx → API Gateway → Order Service
                                    ├─ HTTP → Catalog Service (названия и цены)
                                    └─ HTTP → Payment Service (запуск имитации)

Payment Service → RabbitMQ → Order Service (подтверждение оплаты)
```

1. Клиент получает токен через `POST /api/auth/register` или `POST /api/auth/login`.
2. Клиент получает `product_id` из `GET /api/products` и передаёт его вместе с количеством в `POST /api/orders`.
3. Gateway проверяет JWT и передаёт в Order Service идентификатор пользователя из токена.
4. Order Service получает цены из каталога и сохраняет заказ со статусом `created` и снимком названий и цен товаров.
5. Order Service вызывает внутренний `POST /payments`. Payment Service имитирует оплату, сохраняет `completed` и публикует событие в RabbitMQ.
6. Order Service обрабатывает событие в отдельной сессии БД и сохраняет `paid`. Клиент читает текущий статус через `GET /api/orders/{order_id}`.

## Почему после создания заказа может отображаться created

`POST /api/orders` ждёт HTTP-ответ Payment Service. Ответ содержит состояние заказа из сессии, в которой он был создан. Переход заказа в `paid` выполняется в другой сессии после получения события RabbitMQ. Поэтому ответ создания заказа может показывать `created`, а следующий запрос чтения — `paid`.

`created` означает, что заказ сохранён, а подтверждение оплаты ещё не отражено в прочитанной записи. При сбое доставки или обработки события заказ может остаться в этом статусе даже при платеже `completed`.

## Источники в репозитории

- [README проекта](../README.md)
- [Конфигурация маршрутизации Nginx](../nginx/nginx.conf)
- [Маршруты API Gateway](../api_gateway/app/api/router.py)
- [Создание заказа](../order_service/app/service.py)
- [Имитация оплаты](../payment_service/app/service.py)
