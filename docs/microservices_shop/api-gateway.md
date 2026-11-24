# API Gateway

API Gateway — точка входа в Microservices Shop для клиентских запросов. Nginx передаёт запросы с префиксом `/api/` в FastAPI-приложение. Swagger UI доступен по пути `/api/docs`, схема OpenAPI — по `/api/openapi.json`.

## Внешние маршруты

| Метод и путь | JWT | Назначение |
|---|---|---|
| `POST /api/auth/register` | Нет | Передаёт регистрацию в Auth Service. Успешный ответ — `201` с токеном и данными пользователя. |
| `POST /api/auth/login` | Нет | Передаёт вход в Auth Service. Успешный ответ — `200` с токеном и данными пользователя. |
| `GET /api/auth/me` | Да | Возвращает `id` и `email` из проверенного токена. |
| `GET /api/products` | Нет | Запрашивает список товаров у Catalog Service. |
| `GET /api/products/{product_id}` | Нет | Запрашивает товар по ID у Catalog Service. |
| `POST /api/orders` | Да | Создаёт заказ и запускает имитацию оплаты. Успешный ответ — `201`. |
| `GET /api/orders/{order_id}` | Да | Возвращает заказ текущего пользователя. |

Через gateway каталог доступен для чтения. Создание и удаление товаров относятся к внутреннему API Catalog Service. Маршруты управления платежами и получения списка всех заказов также находятся во внутренних сервисах.

## Как gateway определяет пользователя

Для защищённых маршрутов клиент передаёт заголовок `Authorization: Bearer <access_token>`. Gateway проверяет JWT локально и использует из него `user_id` и `email`. В обработке `GET /api/auth/me` Auth Service не вызывается.

Для `POST /api/orders` текущая схема требует `user_id` в JSON. Gateway заменяет его идентификатором из проверенного JWT перед отправкой заказа в Order Service. Поля позиции заказа — `product_id` и `quantity`.

Для `GET /api/orders/{order_id}` gateway получает заказ из Order Service и сравнивает его `user_id` с идентификатором текущего пользователя. Для чужого заказа gateway возвращает `404` с сообщением `Order not found`.

## Как gateway передаёт ошибки

При сетевой ошибке вызова внутреннего сервиса gateway возвращает `503`. Если внутренний сервис вернул статус `4xx` или `5xx`, gateway передаёт этот статус и включает ответ сервиса в поле `detail`.

## Связанные документы и исходники

- [Вход и регистрация](auth-service.md)
- [Создание и чтение заказа](order-service.md)
- [Роутер Gateway](../api_gateway/app/api/router.py)
- [Модели внешнего API](../api_gateway/app/schemas.py)
- [Проверка JWT](../api_gateway/app/auth.py)
- [Проверка владельца заказа](../api_gateway/app/api/routers/orders.py)
- [Клиент внутренних сервисов](../api_gateway/app/api_client.py)
