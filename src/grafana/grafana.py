from aiohttp import ClientSession
from dotenv import load_dotenv
import os
import datetime
import time
import json

from src.utils import Utils
from src.loger import LogLevel, log_call, log_msg

from src.models import Marketplace, Env
from src.grafana.grafana_exception import GrafanaAuthException
from src.grafana.grafana_api import GrafanaAPI

class GrafanaClient:
    def __init__(self):
        self.cl_session : ClientSession | None = None 
    
    @log_call
    async def async_init(self):
        if Utils.session_alive():
            with open("src/grafana/grafana_config.json", "r") as cfg:
                config = json.load(cfg)
                log_msg(f"{config}", LogLevel.DEBUG.value)
                self.SESSION = config["session"]
        else:
            self.SESSION = await self._auth()
        
        self.COOKIES = {"cookie" : f"grafana_session={self.SESSION}"}
        log_msg(f"{self.COOKIES}", LogLevel.DEBUG.value)

    async def __aenter__(self):
        self.cl_session = ClientSession()
        await self.async_init()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.cl_session:
            await self.cl_session.close()

# ---------------------------------------------------------------------------------→ AUTH ↓

    async def _auth(self):
        """
        Авторизация в Grafana и получение сессионной куки.
        Возвращает значение сессионной куки и записыват ее в конфиг с последней датой жизни сессии в секундах.
        В случае ошибки выбрасывает исключение GrafanaAuthException.
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with GrafanaClient()`")
        
        auth_url = GrafanaAPI.Endpoints.BASE_URL + GrafanaAPI.Endpoints.AUTH_ENDPONT
        
        load_dotenv("creds.env")
        payload = {
            "password": os.getenv("GRAFANA_PASSWORD"),
            "user": os.getenv("GRAFANA_LOGIN")
        }
        async with self.cl_session.post(auth_url, json=payload) as response:
            if response.status != 200:
                data = await response.json()
                msg = "Неверный логин или пароль" if data.get("message") == "Invalid username or password" else data.get("message")
                raise GrafanaAuthException(response.status, response.cookies, f"Ошибка авторизации: {msg}")
            
            grafana_session_cookie = response.cookies.get("grafana_session")
            if not grafana_session_cookie:
                raise GrafanaAuthException(response.status, response.cookies, "Не удалось получить grafana_session")
            
            grafana_session = grafana_session_cookie.value
            grafana_session_max_age = grafana_session_cookie["max-age"] if "max-age" in grafana_session_cookie else None

            last_date = int(datetime.datetime.now().timestamp()) + int(grafana_session_max_age) if grafana_session_max_age else 0

            config = {
                "session": grafana_session,
                "last_date_live": last_date
            }
            with open("src/grafana/grafana_config.json", "w") as cfg:
                cfg.write(json.dumps(config, indent=4))
            
            return grafana_session

# ↑ AUTH ---------------------------------------------------------------------------------→ STORS ↓
    @log_call
    def _gen_stors_payload(self, marketplace: Marketplace):
        """
        Создает запросы для графаны на получение количества ТВЗ в РК МП
        !Возвращает генератор!
        """
        SECONDS_IN_DAY = datetime.timedelta(hours=24).total_seconds()
        sql_map = {
            Env.LTS: GrafanaAPI.SQLRequsts.LTS_STORS_SQL,
            Env.LATEST: GrafanaAPI.SQLRequsts.LATEST_STORS_SQL,
            Env.POLZA: GrafanaAPI.SQLRequsts.POLZA_STORS_SQL
        }
        
        # Получаем базовый SQL запрос для окружения
        base_sql = sql_map[marketplace.env]
        
        for region in marketplace.regions:
            # Форматируем SQL с обоими параметрами сразу
            formatted_sql = base_sql.format(
                org_id=str(region.id), 
                mp_id=str(marketplace.id)
            )
            
            payload = {
                "queries": [
                    {
                        "refId": f"{region.name}",
                        "datasource": GrafanaAPI.Sources.DHW_CLICKHOUSE_DATASOURCE,
                        "rawSQL": formatted_sql,  # Используем уже отформатированный SQL
                        "format": 1,
                        "maxDataPoints": 1384
                    }
                ],
                "range": {
                    "from": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                    "to": datetime.datetime.now().isoformat(),
                    "raw": {
                        "from": "now-24h",
                        "to": "now"
                    }
                },
                "from": f"{time.time() - SECONDS_IN_DAY}",
                "to": f"{time.time()}"
            }

            yield payload, region.name
    
    @log_call
    async def get_count_stors(self, marketplace: Marketplace) -> dict[str, str]:
        """
        Прокидывает SQL query в Grafana и получает количество ТВЗ для каждого РК маркетплейса
        
        Args:
            marketplace (Marketplace): маркетплейс для которого будет получение ТВЗ
        Returns:
            dict: словарь где имя РК - ключ, а значение - количество ТВЗ 
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with GrafanaClient()`")
        url = f"{GrafanaAPI.Endpoints.BASE_URL}{GrafanaAPI.Endpoints.QUERY_ENDPOINT}"
        header = {"Content-Type": "application/json"}
        header["cookie"] = self.COOKIES.get("cookie", "")
        
        payloads = self._gen_stors_payload(marketplace=marketplace)
        stors = {}
        for payload, name in payloads:
            async with self.cl_session.post(url=url, headers=header, json=payload) as resp:
                res = await resp.json()
                log_msg(f"{res}", LogLevel.DEBUG.value)
                if resp.status == 200:
                    results = res.get("results") or {}
                    region_resp = results.get(name) or {}
                    
                    # Получаем frames из ответа
                    frames = region_resp.get("frames") or []
                    if frames:
                        # Берем первый frame
                        frame = frames[0]
                        data = frame.get("data") or {}
                        values = data.get("values") or []
                        
                        # Данные находятся в values[0][0]
                        if values and len(values) > 0 and len(values[0]) > 0:
                            stors[name] = values[0][0]
                        else:
                            stors[name] = "Нет данных"
                    else:
                        stors[name] = "Нет данных"
                else:
                    stors[name] = f"Не удалось получить ответ → Статус запроса: {resp.status}"
        
        return stors

# ↑ STORS ---------------------------------------------------------------------------------→ CACHE ↓
    @log_call
    def _gen_cache_payload(self, marketplace : Marketplace, details : bool = False) -> dict:
        """
        Создает запрос для получения кэша по МП

        Params:
            marketplac(Marketplace) : МП для которого будет составлятся запрос
            details(bool) : Если указан True - вернет запрос который вернет детальную статистику кэша
        Returns:
            dict: Запрос

        """
        SECONDS_IN_6HORS = datetime.timedelta(hours=6).total_seconds() # 6 часов стоит в запросе дашборда, подозреваю что связано с тем что обмен остатков в кэш происходит раз в 6 часов
        sources_map = {
            Env.LTS : GrafanaAPI.Sources.LTS_POSTGRES_DATASOURCE,
            Env.LATEST : GrafanaAPI.Sources.LATEST_POSTGRES_DATASOURCE,
            Env.POLZA : GrafanaAPI.Sources.POLZA_POSTGRES_DATASOURCE
        }
        if not details:
            payload = {"queries" : [
                    {
                        "refId" : "A", # стандартный refId графаны
                        "datasource" : sources_map[marketplace.env],
                        "rawSQL" : GrafanaAPI.SQLRequsts.CACHE_SQL.format(mp_guid = f"'{marketplace.guid}'"),
                        "format" : "table",
                        "maxDataPoints" : 1384
                    }
                ],
                "range" : {
                    "from" : (datetime.datetime.now() - datetime.timedelta(hours=6)).isoformat(),
                    "to" : datetime.datetime.now().isoformat(),
                    "raw" : {
                        "from" : "now-6h",
                        "to" : "now"
                    }
                },
                "from" : f"{time.time() - SECONDS_IN_6HORS}",
                "to" : f"{time.time()}"
            }

            return payload
        else:
            payload = {"queries" : [
                    {
                        "refId" : "A", # стандартный refId графаны
                        "datasource" : sources_map[marketplace.env],
                        "rawSQL" : GrafanaAPI.SQLRequsts.DITAILS_CACHE_SQL.format(mp_name = marketplace.name),
                        "format" : 1,
                        "maxDataPoints" : 1384
                    }
                ],
                "range" : {
                    "from" : (datetime.datetime.now() - datetime.timedelta(hours=6)).isoformat(),
                    "to" : datetime.datetime.now().isoformat(),
                    "raw" : {
                        "from" : "now-6h",
                        "to" : "now"
                    }
                },
                "from" : f"{time.time() - SECONDS_IN_6HORS}",
                "to" : f"{time.time()}"
            }
            return payload

    @log_call
    async def get_status_cache(self, marketplace: Marketplace) -> str | tuple[str, dict]:
        """
        Запрашивает статус кэша остатков.  
        Если статус не `SUCCESS`, дополнительно получает детальную статистику по кэшу в каждом РК маркетплейса.
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with GrafanaClient()`")
        
        url = f"{GrafanaAPI.Endpoints.BASE_URL}{GrafanaAPI.Endpoints.QUERY_ENDPOINT}"
        header = {"Content-Type": "application/json"}
        header["cookie"] = self.COOKIES.get("cookie", "")
        
        payload = self._gen_cache_payload(marketplace)
        
        # Логируем payload для отладки
        log_msg(f"Payload для кэша: {json.dumps(payload, indent=2)}", LogLevel.DEBUG.value)
        
        async with self.cl_session.post(url=url, headers=header, json=payload) as resp:
            # Получаем текст ответа для отладки
            response_text = await resp.text()
            log_msg(f"Response status: {resp.status}, Response: {response_text}", LogLevel.DEBUG.value)
            
            if resp.status == 200:
                try:
                    res = await resp.json()
                    results = res.get("results") or {}
                    region_resp = results.get("A") or {}
                    
                    # Получаем frames из ответа
                    frames = region_resp.get("frames") or []
                    if frames:
                        frame = frames[0]
                        data = frame.get("data") or {}
                        values = data.get("values") or []
                        
                        if values and len(values) > 0 and len(values[0]) > 0:
                            cache_status = values[0][0]
                        else:
                            cache_status = "Нет данных"
                    else:
                        cache_status = "Нет данных"

                    if cache_status != "SUCCESS":
                        # Получаем детальную статистику
                        payload_details = self._gen_cache_payload(marketplace, details=True)
                        details_cache = {}
                        
                        async with self.cl_session.post(url=url, headers=header, json=payload_details) as details_resp:
                            details_response_text = await details_resp.text()
                            log_msg(f"Details response status: {details_resp.status}, Response: {details_response_text}", LogLevel.DEBUG.value)
                            
                            if details_resp.status == 200:
                                details_res = await details_resp.json()
                                details_results = details_res.get("results") or {}
                                details_region_resp = details_results.get("A") or {}
                                details_frames = details_region_resp.get("frames") or []
                                
                                if details_frames:
                                    details_frame = details_frames[0]
                                    details_data = details_frame.get("data") or {}
                                    details_values = details_data.get("values") or []
                                    
                                    if details_values and len(details_values) >= 4:
                                        regions = details_values[0]  # org_name
                                        db_counts = details_values[1]  # db_count
                                        cache_counts = details_values[2]  # cache_count
                                        percents = details_values[3]  # percent

                                        for region, db_count, cache_count, percent in zip(regions, db_counts, cache_counts, percents):
                                            details_cache[region] = {
                                                "db": db_count,
                                                "cache": cache_count,
                                                "%": percent
                                            }
                                        
                                        return cache_status, details_cache
                            
                            log_msg("Не удалось получить детальную статистику → вернул только статус", LogLevel.WARN.value)
                            return cache_status
                    else:
                        return cache_status
                        
                except Exception as e:
                    log_msg(f"Ошибка парсинга ответа: {e}", LogLevel.ERORR.value)
                    return f"Ошибка парсинга ответа: {e}"
            else:
                return f"Не удалось получить ответ → Статус запроса: {resp.status}\nResponse: {response_text}"

# ↑ CACHE ---------------------------------------------------------------------------------→ EXCHANGES ↓
    @log_call
    async def _gen_msearch_payload(self, marketplace : Marketplace, min : int, elk_req_map : dict) -> str:
        """
        Создает тело для /_msearch запроса.

        Args:
            marketplace(Marketplace) : маркетплейс
            min(int) : минуты для открезка времени от текущего до текущее минус указаные минуты
            elk_req_map : словарь где Env ключ, а LuceneRequestes значение
        Returns:
            str : запрос для /_msearch
        """
        elk_sources_map = {
            Env.LTS : GrafanaAPI.Sources.ELK_LTS_SOURCE,
            Env.LATEST : GrafanaAPI.Sources.ELK_LATEST_SOURCE
        }
        
        header = {"index" : elk_sources_map[marketplace.env]}
        body = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                "gte": int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=min)).timestamp() * 1000), # сейчас - временной отрезок = стартовое время и умножаем на 1000 что бы было в миллисекундах
                                "lte": int((datetime.datetime.now(datetime.timezone.utc)).timestamp() * 1000) # сейчас в миллисекундах 
                                }
                            }
                        },
                        {
                            "query_string": {
                                "query" : f"{elk_req_map[marketplace.env.value].format(mp_name = marketplace.elk_name)}"
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "2": {
                "date_histogram": {
                    "field": "@timestamp",
                    "min_doc_count": 0,
                    "extended_bounds": {
                    "min": int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=min)).timestamp() * 1000), # сейчас - временной отрезок = стартовое время и умножаем на 1000 что бы было в миллисекундах,
                    "max": int((datetime.datetime.now(datetime.timezone.utc)).timestamp() * 1000) # сейчас в миллисекундах 
                    },
                    "format": "epoch_millis",
                    "fixed_interval": "300000ms"
                },
                "aggs": {}
                }
            }
        }

        payload = f"{json.dumps(header)}\n{json.dumps(body)}" + '\n'
        return payload
    
    @log_call
    async def get_value_exchanges_by_req(self, marketplace : Marketplace, elk_req_map : dict, time_map : list[int] | None = None) -> tuple[int|str, int]:
        """
        Прокидывает Lucene запрос в ELK и возвращает значение количества hits и временной промежуток за который hits стало > 0

        Args:
            marketplace(Marketplace): маркетплейс
            elk_req_map(dict): Словарь запросов где Env ключ, а LuceneRequestes значение
            time_map(list[int]): Лист с количеством минут для временного отрезка за который будет прокидываться запрос
                - В начале листа указывается наименьший временной промежуток, дальше по возрастанию
                - Если не будет указан - поиск будет происходить по стандартному листу:
                    * 5 минут
                    * 10 минут
                    * 15 минут
                    * 30 минут
                    * 60 минут (1 час)
                    * 120 минут (2 часа)
                    * 240 минут (4 часа)
                    * 360 минут (6 часов)
                    * 720 минут (12 часов)
                    * 1440 минут (24 часа)
        Returns:
            tuple[int|str, int]: 
                - hits и временной промежуток (в минутах) за который hits стало > 0
                - Вместо hits может быть строка если статус запроса оказался != 200
                - Если за все время не будет найдено ни одного hit - вернется 0 и последний временной промежуток.

        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with GrafanaClient()`")
        
        elk_sources_id_map = {
            Env.LTS : GrafanaAPI.Sources.ELK_LTS_SOURCE_ID,
            Env.LATEST : GrafanaAPI.Sources.ELK_LATEST_SOURCE_ID
        }

        url = f"{GrafanaAPI.Endpoints.BASE_URL}{GrafanaAPI.Endpoints.ELK_MULTI_SEARCH_ENDPOINT.format(source_id = elk_sources_id_map[marketplace.env])}"
        print(url)
        header = {"Content-Type" : "application/x-ndjson"}
        header["cookie"] = self.COOKIES.get("cookie", "")

        if not time_map: # если не указано
            time_map = [5, 10, 15, 30, 60, 120, 240, 360, 720, 1440]
        
        for span in time_map:
            payload = await self._gen_msearch_payload(marketplace, span, elk_req_map)
            
            async with self.cl_session.post(url=url, headers=header, data=payload) as resp:
                res = await resp.json()
                if resp.status == 200:
                    responses = res.get("responses") or []
                    response = responses[0] or {}
                    hits = response.get("hits") or {}
                    total = hits.get("total") or {}
                    value = total.get("value") or -1
                    if value == 0:
                        continue
                    elif value == -1:
                        log_msg(f"Не удалось получить ответ → Статус запроса: {resp.status}, Responce: {responses}", LogLevel.WARN.value)
                    else:
                        return value, span
                else:
                    value = f"Не удалось получить ответ → Статус запроса: {resp.status}, Responce: {await resp.text()}"
        return value, span

# ↑ EXCHANGES ---------------------------------------------------------------------------------→ QUERIES ↓

    async def get_queries(self):
        ...
