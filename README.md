# E-Commerce Monitoring System - Полная документация

## 🏗️ Архитектура системы

### Общее описание
Система представляет собой комплексный мониторинг e-commerce маркетплейсов с интеграцией двух основных платформ:
- **Grafana** - для сбора технических метрик и производительности
- **Redash** - для бизнес-аналитики и отчетности

Система построена на асинхронной архитектуре с использованием `aiohttp` для эффективной работы с сетевыми запросами.

---

## 📊 Модели данных

### 🔧 BaseModel (Pydantic)
Все модели наследуются от `BaseModel` Pydantic, что обеспечивает:
- Валидацию типов данных
- Сериализацию/десериализацию JSON
- Автодокументацию

### 🏪 Marketplace
```python
class Marketplace(BaseModel):
    active: bool              # Активен ли маркетплейс
    id: int                   # Уникальный ID в БД
    guid: str                 # GUID маркетплейса
    name: str                 # Название (должно совпадать с БД)
    elk_name: str             # Имя для ELK запросов
    regions: list[Region]     # Список регионов
    env: Env                  # Окружение (LTS/LATEST/POLZA)
```

### 🌍 Region (Enum)
Перечисление всех региональных подразделений компании:

| Регион | Компания                 | ID  | Город        |
| ------ | ------------------------ | --- | ------------ |
| MSK    | ООО "ФК ПУЛЬС"           | 1   | Москва       |
| YRS    | ООО "ПУЛЬС Ярославль"    | 2   | Ярославль    |
| BRN    | ООО "ПУЛЬС Брянск"       | 4   | Брянск       |
| SPB    | ООО "ПУЛЬС СПб"          | 5   | СПб          |
| VLG    | ООО "ПУЛЬС Волгоград"    | 6   | Волгоград    |
| VRN    | ООО "ПУЛЬС Воронеж"      | 7   | Воронеж      |
| KZN    | ООО "ПУЛЬС Казань"       | 8   | Казань       |
| KRN    | ООО "ПУЛЬС Краснодар"    | 9   | Краснодар    |
| HBR    | ООО "ПУЛЬС Хабаровск"    | 10  | Хабаровск    |
| IRK    | ООО "ПУЛЬС Иркутск"      | 11  | Иркутск      |
| KRS    | ООО "ПУЛЬС Красноярск"   | 12  | Красноярск   |
| EKB    | ООО "ПУЛЬС Екатеринбург" | 13  | Екатеринбург |
| NSK    | ООО "ПУЛЬС Новосибирск"  | 14  | Новосибирск  |
| SAM    | ООО "ПУЛЬС Самара"       | 15  | Самара       |

### 📦Маркетплейсы (их id)

| id    | name                        |
| ----- | --------------------------- |
| `100` | `Фармаимпекс`               |
| `99`  | `АйтиКакая Аптека Даркстор` |
| `98`  | `Все аптеки - Яндекс.Еда`   |
| `97`  | `Яндекс ДСМ Даркстор`       |
| `96`  | `Wildberries ДСМ Даркстор`  |
| `94`  | `Губернские Аптеки`         |
| `93`  | `Wildberries C&C`           |
| `91`  | `Справмедика`               |
| `88`  | `Хелло.док`                 |
| `87`  | `Озон FBO`                  |
| `86`  | `Wildberries FBO`           |
| `83`  | `Первый электронный рецепт` |
| `72`  | `Магнит Аптека`             |
| `71`  | `Wildberries ДСМ`           |
| `70`  | `Эркафарм`                  |
| `69`  | `Здоровый город`            |
| `63`  | `СберМаркет`                |
| `62`  | `СберМаркет.Доставка`       |
| `61`  | `Сбермегамаркет FBS`        |
| `60`  | `Максавит`                  |
| `59`  | `ecom-client-polza`         |
| `58`  | `Амурфармация`              |
| `57`  | `Яндекс NDD`                |
| `56`  | `АналитФармация`            |
| `52`  | `ЯндексFBS`                 |
| `51`  | `WildberriesFBS`            |
| `50`  | `Ютека ДСМ`                 |
| `47`  | `Сбермегамаркет ДСМ`        |
| `46`  | `Яндекс.Доставка`           |
| `45`  | `Артэс`                     |
| `44`  | `Здравсервис`               |
| `43`  | `ОК Аптека`                 |
| `39`  | `АптекаМос`                 |
| `38`  | `АЛОЭ`                      |
| `37`  | `Фармэконом`                |
| `36`  | `Мед-Сервис`                |
| `35`  | `Сбермегамаркет`            |
| `33`  | `Вита-Плюс`                 |
| `32`  | `Гармония здоровья`         |
| `31`  | `Мегаптека`                 |
| `30`  | `009.рф`                    |
| `29`  | `В аптеке`                  |
| `28`  | `ЯндексDBS`                 |
| `27`  | `Вита Норд`                 |
| `26`  | `Озон RFBS`                 |
| `25`  | `ЦВА`                       |
| `17`  | `Народная аптека`           |
| `16`  | `Невис`                     |
| `15`  | `Планета Здоровья`          |
| `13`  | `Фармия`                    |
| `12`  | `НЕ ИСПОЛЬЗОВАТЬ`           |
| `11`  | `Озон`                      |
| `10`  | `Все аптеки`                |
| `9`   | `ЕАптека-маркетплейс`       |
| `8`   | `Аптечная сеть НеоФарм`     |
| `6`   | `Аптечная сеть 36,6`        |
| `5`   | `Ютека`                     |
| `4`   | `Созвездие. Не Еком`        |
| `3`   | `АптекаФорте`               |
| `2`   | `ЕАптека`                   |
| `1`   | `АСНА`                      |

### 📦Маркетплейсы (их user name в ELK)
Их названия можете найти на дашбордах. 
Абсолютное большинство которое Вам необходимо можно найти на "ECOM SLA"

**Использование:**
```python
region = Region.MSK
print(region.company_name)  # ООО "ФК ПУЛЬС"
print(region.id)           # 1
print(region.city)         # Москва
```

### 🎯 Env (Enum)
Окружения системы:
- `LTS` - Long Term Support (стабильная версия)
- `LATEST` - Последняя версия
- `POLZA` - Специальное окружение

---

## 🔐 Grafana Client

### 📍 Endpoints
```python
class Endpoints:
    BASE_URL = "https://grafana02.puls.ru"
    
    # Аутентификация
    AUTH_ENDPOINT = "/login"
    
    # Запросы к данным
    ELK_MULTI_SEARCH_ENDPOINT = "/api/datasources/proxy/{source_id}/_msearch"
    ELK_SEARCH_ENDPOINT = "/api/datasources/proxy/{source_id}/_search"
    QUERY_ENDPOINT = "/api/ds/query"
```

### 🗃️ Источники данных (Data Sources)

#### PostgreSQL источники:
- `LATEST_POSTGRES_DATASOURCE` - UID: "LRv7BwRNk"
- `LTS_POSTGRES_DATASOURCE` - UID: "NZ6mrUSSz" 
- `POLZA_POSTGRES_DATASOURCE` - UID: "bgCdmzHIk"

#### ClickHouse источники:
- `DHW_CLICKHOUSE_DATASOURCE` - UID: "z4ICaIsIz"

#### Prometheus источники:
- `LTS_VICTORIA_METRICS_DATASOURCE` - для Celery метрик LTS
- `LATEST_PROMETHEUS_DATASOURCE` - прометеус latest
- `POLZA_PROMETHEUS_DATASOURCE` - прометеус polza
- `BFF_PROMETHEUS_DATASOURCE` - прометеус BFF

#### ELK источники:
- `ELK_LTS_SOURCE` - "apm-*prod-ecom*"
- `ELK_LATEST_SOURCE` - "apm-*prod-latest-ecom*"

### 📊 SQL Запросы

#### Запросы количества магазинов:
```sql
-- LTS
SELECT uniqExact(`after.marketplace_store_id`) 
FROM `default`.`ecom-lts.debezium.cdc.public.delivery_organizationaddress` oa
INNER JOIN `default`.`ecom-lts.debezium.cdc.public.delivery_marketplacestore` ms 
ON oa.`after.marketplace_store_id` = ms.`after.id` 
WHERE ms.`after.is_active` 
AND `after.organization_id` = {org_id} 
AND `after.marketplace_id` = {mp_id}
```

#### Запросы кэша остатков:
```sql
-- Детальная статистика
SELECT DISTINCT ON (s.org_name, mm.name, s.marketplace_guid) 
    s.org_name, s.db_count, s.cache_count, s.percent 
FROM statistic_nonzerostockmetric s 
INNER JOIN marketplace_marketplace mm 
    ON mm.guid = s.marketplace_guid::uuid 
    AND mm.name = {mp_name} 
WHERE s.actual = true 
ORDER BY s.org_name, s.marketplace_guid;

-- Статус кэша
SELECT status 
FROM statistic_nonzerostockmetricstatus 
WHERE actual=True 
AND marketplace_guid={mp_guid};
```

### 🔍 Lucene запросы для ELK

#### Заказы:
```lucene
# LTS
processor.event:"transaction" 
AND service.environment: "prod" 
AND (url.path: "/v1.0/orders" 
    OR transaction.name: *YandexOrderAcceptView* 
    OR transaction.name: *SbermmOrderNewView*
    OR transaction.name: *BaseImportOrderService*
    OR transaction.name: *OrderView_for_garmoniya*) 
AND user.name: {mp_name}
```

#### Остатки:
```lucene
# LATEST  
((processor.event:"transaction" 
AND service.environment: selectel-prod-latest 
AND (transaction.name:/.*stock_changes.*/ 
    OR transaction.name: *api\/products\/stocks*  
    OR transaction.name:*offers\/stocks* )) 
OR (transaction.name: /.*GET.*Stock.*/ AND http.response.status_code: 200) 
OR (transaction.name:/.*seller.*/ AND transaction.name:/.*stocks.*/) 
OR (transaction.name: *api.aptekamos.ru\/Price\/WPrice\/WimportPrices*) 
OR (transaction.name: *\/api\/v3\/stocks\/*)) 
AND service.name: ("ecom" OR "ecom-polza") 
AND user.name: {mp_name}
```

### 🚀 Основные методы GrafanaClient

#### 🔐 Аутентификация
```python
async def _auth(self) -> str:
    """
    Авторизация в Grafana с получением сессионной куки.
    Сохраняет сессию в grafana_config.json с временем жизни.
    """
```

#### 🏪 Получение количества магазинов
```python
async def get_count_stors(self, marketplace: Marketplace) -> dict[str, str]:
    """
    Получает количество ТВЗ (торгово-закупочных точек) для каждого региона.
    
    Returns:
        dict: { "MSK": "150", "SPB": "89", ... }
    """
```

#### 💾 Статус кэша остатков
```python
async def get_status_cache(self, marketplace: Marketplace) -> str | tuple[str, dict]:
    """
    Проверяет статус кэша остатков. Если статус не SUCCESS, 
    возвращает детальную статистику по регионам.
    
    Returns:
        - "SUCCESS" - если все ок
        - ("FAILED", details) - если проблемы, с детальной статистикой
    """
```

#### 📈 Метрики обменов
```python
async def get_value_exchanges_by_req(self, marketplace: Marketplace, 
                                   elk_req_map: dict, 
                                   time_map: list[int] = None) -> tuple[int|str, int]:
    """
    Получает количество событий обменов (hits) в ELK за различные временные промежутки.
    
    Args:
        elk_req_map: Словарь Lucene запросов по окружениям
        time_map: Промежутки времени в минутах [5, 10, 15, ...]
    
    Returns:
        tuple: (количество hits, промежуток в минутах)
    """
```

---

## 📈 Redash Client

### 📍 Endpoints Redash
```python
class Endpoints:
    BASE_URL = "https://redash.polza.ru"
    
    # Управление задачами
    START_JOB_ENDPOINT = "/api/queries/{query}/results"
    GET_STATUS_JOB_ENDPOINT = "/api/jobs/"
    GET_RESULT_JOB_ENDPOINT = "/api/query_results/{query_result_id}"
    
    # SQL запросы
    START_SQL_JOB = "/api/query_results"
```

### 📊 Статусы задач (JobStatus)
- `PENDING = 1` - Ожидание
- `STARTED = 2` - Выполняется  
- `SUCCESS = 3` - Успешно
- `FAILURE = 4` - Ошибка
- `CANCELLED = 5` - Отменено

### 📋 Готовые запросы

#### Расписания:
```json
{
    "id": 8862,
    "parameters": {
        "Маркетплейс": "{mp_name}",
        "РК": "{reg_name}", 
        "Регион": ["Bce регионы"]
    },
    "apply_auto_limit": false,
    "max_age": 0
}
```

#### Проблемные регионы:
```json
{
    "id": 9021,
    "parameters": {
        "marketplace_name": "{mp_name}"
    },
    "apply_auto_limit": false, 
    "max_age": 0
}
```

#### Расхождения магазинов 1С/ECOM:
```sql
WITH b AS (
    SELECT marketplace_id, rk_id, rk, addressguid, tvz_1c, tvz_ec 
    FROM cached_query_8437 
    WHERE marketplace_id = {mp_id}
)
SELECT 
    0 as "РК id",
    'Все РК' as "РК", 
    count(tvz_1c) as "1С",
    count(tvz_ec) as "Ecom",
    sum(case when tvz_1c > 0 and tvz_ec is null then 1 else 0 end) || ' / ' || 
    sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end) as "Отсутствуют/Лишние (Ecom-1С)",
    coalesce(round((sum(case when tvz_1c = tvz_ec then 1 else 0 end) - 
           sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end)) * 100.0 / 
           count(tvz_1c), 2), 0.00) as "Доля схождений",
    datetime('now','+3 hour') as dt
FROM b
UNION
SELECT 
    rk_id, rk,
    count(tvz_1c) as tvz_1c,
    count(tvz_ec) as tvz_ec,
    sum(case when tvz_1c > 0 and tvz_ec is null then 1 else 0 end) || ' / ' || 
    sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end) as lc_ec,
    coalesce(round((sum(case when tvz_1c = tvz_ec then 1 else 0 end) - 
           sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end)) * 100.0 / 
           count(tvz_1c), 2), 0.00) as lc_ec_p,
    datetime('now','+3 hour') as dt
FROM b
WHERE rk is not null and rk <> 'Нет инфо'
GROUP BY rk_id, rk
```

### 🚀 Основные методы RedashClient

#### 🔄 Управление задачами
```python
async def check_status_job(self, job_id: str) -> tuple[int, int]:
    """
    Отслеживает статус задачи до завершения.
    Возвращает (статус, query_result_id).
    """

async def start_job(self, body: dict, url: str = ..., query: int = None) -> str:
    """
    Запускает задачу. Поддерживает перегрузку для разных типов запросов.
    """
```

#### 📊 Бизнес-метрики
```python
async def get_schedules_by_mp(self, marketplace: Marketplace) -> dict[str, int]:
    """
    Количество сформированных расписаний по регионам.
    """

async def get_info_about_problem_regions(self, marketplace: Marketplace) -> list[dict]:
    """
    Статистика по проблемным регионам с динамикой заказов.
    Возвращает: [{"region": "MSK", "value": 150, "change": "-9.81% ↓"}, ...]
    """

async def get_info_about_history(self, marketplace: Marketplace) -> dict:
    """
    Исторические данные заказов за последние 30 дней.
    Группирует по дням недели (все понедельники, все вторники и т.д.)
    """

async def get_info_discrepancy_stors_by_regions(self, marketplace: Marketplace) -> dict:
    """
    Расхождения между количеством магазинов в 1С и Ecom системе.
    """
```

---

### 📁 Управление конфигурацией

#### Формат конфигурации (JSON Lines):
```json
{"active": true, "id": 1, "guid": "mp1-guid", "name": "wildberries", "elk_name": "wildberries", "regions": ["MSK", "SPB"], "env": "LTS"}
{"active": true, "id": 2, "guid": "mp2-guid", "name": "ozon", "elk_name": "ozon", "regions": ["MSK", "EKB"], "env": "LATEST"}
```

#### Методы:
```python
@staticmethod
def read_config(file_path: str = "marcetplaces_config.jsonl") -> list[Marketplace]:
    """
    Читает и валидирует конфигурацию маркетплейсов.
    """

@staticmethod  
def add_marketplace_to_config(marketplace_data: dict, file_path: str = ...) -> bool:
    """
    Добавляет новый маркетплейс в конфиг с валидацией.
    """

@staticmethod
def create_marketplace_interactively(file_path: str = ...) -> bool:
    """
    Интерактивное создание маркетплейса через консоль.
    """
```

### 🔐 Управление сессиями
```python
@staticmethod
def session_alive() -> bool:
    """
    Проверяет активность сессии Grafana по времени жизни.
    Использует grafana_config.json для хранения данных сессии.
    """
```

---

## 🎯 Примеры использования

### 📊 Полный мониторинг маркетплейса
```python
import asyncio
from src.grafana.grafana_client import GrafanaClient
from src.redash.redash_client import RedashClient
from src.models import Marketplace, Env
from src.regions import Region

async def full_monitoring():
    marketplace = Marketplace(
        active=True,
        id=1,
        guid="wildberries-guid",
        name="wildberries",
        elk_name="wildberries", 
        regions=[Region.MSK, Region.SPB, Region.EKB],
        env=Env.LTS
    )
    
    async with GrafanaClient() as grafana, RedashClient() as redash:
        # Технические метрики
        stores = await grafana.get_count_stors(marketplace)
        cache_status = await grafana.get_status_cache(marketplace)
        
        # Бизнес метрики
        schedules = await redash.get_schedules_by_mp(marketplace)
        problem_regions = await redash.get_info_about_problem_regions(marketplace)
        discrepancies = await redash.get_info_discrepancy_stors_by_regions(marketplace)
        
        return {
            "stores": stores,
            "cache": cache_status,
            "schedules": schedules, 
            "problems": problem_regions,
            "discrepancies": discrepancies
        }

# Запуск
result = asyncio.run(full_monitoring())
print(result)
```

### ➕ Добавление нового маркетплейса
```python
from src.utils import Utils

# Программно
new_mp = {
    "active": True,
    "id": 3, 
    "guid": "new-mp-guid",
    "name": "yandex_market",
    "elk_name": "yandex_market",
    "regions": ["MSK", "SPB", "KZN"],
    "env": "LATEST"
}
Utils.add_marketplace_to_config(new_mp)

# Интерактивно
Utils.create_marketplace_interactively()
```

---

## 🚨 Обработка ошибок

### Исключения Grafana
```python
class GrafanaAuthException(GrafanaException):
    """
    Ошибки аутентификации (неверный логин/пароль)
    """

class GrafanaRequestException(GrafanaException):  
    """
    Ошибки запросов (неверные параметры, недоступность и т.д.)
    """
```

### Логирование
Уровни логирования:
- `INFO` - Информационные сообщения
- `SUCCESS` - Успешные операции
- `WARN` - Предупреждения
- `ERROR` - Ошибки

```python
log_msg("Сообщение", LogLevel.INFO.value)
```

---

## 📁 Структура проекта (фундламент)
```
src/
├── models/                    # Модели данных
│   ├── __init__.py
│   └── marketplace.py        # Marketplace, Env, StoresData, etc.
├── regions/                  # Регионы компании
│   ├── __init__.py
│   └── region.py            # Region enum
├── grafana/                  # Grafana клиент
│   ├── __init__.py
│   ├── grafana_api.py       # Endpoints, Sources, SQL/PQL запросы
│   ├── grafana_client.py    # Основной клиент
│   └── grafana_exception.py # Исключения
├── redash/                   # Redash клиент  
│   ├── __init__.py
│   ├── redash_api.py        # Endpoints, QueryBody
│   └── redash_client.py     # Основной клиент
├── utils/                    # Утилиты
│   ├── __init__.py
│   └── utils.py             # Utils класс
└── loger/                   # Логирование
    ├── __init__.py
    └── loger.py             # log_msg, log_call, LogLevel
```

---

## 🔧 Конфигурационные файлы

### grafana_config.json
```json
{
    "session": "grafana_session_cookie_value",
    "last_date_live": 1738857600
}
```

### marcetplaces_config.jsonl
```
{"active": true, "id": 1, "guid": "mp1", "name": "wb", ...}
{"active": true, "id": 2, "guid": "mp2", "name": "ozon", ...}
```

### creds.env
```
GRAFANA_LOGIN=user@company.com
GRAFANA_PASSWORD=password123
REDASH_API_KEY=api_key_here
```

---
## 🔄 ПОЛНЫЙ WORKFLOW АНАЛИТИКИ
### Последовательность выполнения:
Выбор маркетплейса из конфигурации
#### Сбор технических метрик (Grafana):
Количество ТВЗ по регионам (get_count_stors)
Статус кэша остатков (get_status_cache)
Метрики обменов (get_value_exchanges_by_req):
- Заказы (orders)
- Остатки (stocks)
- Цены (prices)
#### Сбор бизнес-метрик (Redash):
Исторические данные заказов (get_info_about_history)
Проблемные регионы (get_info_about_problem_regions)
Расписания доставки (get_schedules_by_mp)
Расхождения ТВЗ (get_info_discrepancy_stors_by_regions)
Формирование отчета (_create_report)

---

## 💡 Особенности реализации

### Асинхронность
- Все сетевые запросы используют `async/await`
- Контекстные менеджеры для управления сессиями
- Параллельное выполнение независимых запросов

### Валидация данных
- Pydantic модели для строгой типизации
- Валидация на уровне методов
- Обработка ошибок форматов

### Расширяемость
- Модульная архитектура
- Легкое добавление новых источников данных
- Поддержка различных типов запросов

### Безопасность
- Хранение учетных данных в .env файле
- Управление сессиями с временем жизни
- Валидация входных данных

### TODO
- дописать проверку очередей тасок через API Grafana
