from dotenv import load_dotenv
import os

from loger import log_call, log_msg, LogLevel
from models import Marketplace
from aiohttp import ClientSession
from redash.redash_api import RedashAPI
from typing import overload
import asyncio
import re
import json
import datetime

class RedashClient:
    async def async_init(self):
        load_dotenv("creds.env")
        self.API_KEY = os.getenv("REDASH_API_KEY")
        self.AUTH_HEADER = {"Authorization" : f"Key {self.API_KEY}"}

    async def __aenter__(self):
        self.cl_session = ClientSession()
        await self.async_init()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.cl_session:
            await self.cl_session.close()

    # ---------------------------------------------------------------------------
    @log_call 
    async def check_status_job(self, job_id: str) -> tuple[int, int]:
        """
        Проверяет статус работы Job'а пока тот не отработает/отменится/упадет.
        
        Args:
            job_id(str): Job id который будет проверятся
        Returns:
            tuple[int, int]:
                - Если запрос прошел успешно: возвращает 3 и query_result_id
                - Если запрос не удачный: возвращает 4/5 и 0 как query_result_id
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with RedashClient()`")

        # Правильно формируем URL - job_id должен быть частью пути, а не query параметром
        url = f"{RedashAPI.Endpoints.BASE_URL}{RedashAPI.Endpoints.GET_STATUS_JOB_ENDPOINT}{job_id}"
        
        log_msg(f"Проверка статуса job: {url}", LogLevel.INFO.value)

        status = RedashAPI.JobStatus.STARTED.value
        query_result_id = 0
        
        while status not in [RedashAPI.JobStatus.SUCCESS.value, RedashAPI.JobStatus.FAILURE.value, RedashAPI.JobStatus.CANCELLED.value]:
            try:
                async with self.cl_session.get(url=url, headers=self.AUTH_HEADER) as resp:
                    # Сначала проверяем content-type
                    content_type = resp.headers.get('Content-Type', '')
                    if 'application/json' not in content_type:
                        # Если это не JSON, читаем как текст для отладки
                        text_response = await resp.text()
                        log_msg(f"Неожиданный content-type: {content_type}. Response: {text_response[:200]}", LogLevel.WARN.value)
                        
                        if resp.status == 200:
                            # Пробуем парсить как JSON даже если content-type неправильный
                            try:
                                res = await resp.json()
                            except:
                                # Если не получается, создаем пустой результат
                                res = {}
                        else:
                            res = {}
                    else:
                        res = await resp.json()
                    
                    if resp.status == 200:
                        job = res.get('job') or {"status": RedashAPI.JobStatus.PENDING.value}
                        status = job['status']
                        
                        if status == RedashAPI.JobStatus.SUCCESS.value:
                            log_msg("Job отработал!", LogLevel.SUCCESS.value)
                            query_result_id = job.get('query_result_id') or 0
                            break
                        
                        elif status in [RedashAPI.JobStatus.FAILURE.value, RedashAPI.JobStatus.CANCELLED.value]:
                            log_msg(f"Job в статусе {RedashAPI.JobStatus(status).name}", 
                                    LogLevel.WARN.value if status == RedashAPI.JobStatus.CANCELLED.value else LogLevel.ERORR.value)
                            query_result_id = 0
                            break
                        
                        elif status in [RedashAPI.JobStatus.STARTED.value, RedashAPI.JobStatus.PENDING.value]:
                            log_msg(f"Job работает, статус: {RedashAPI.JobStatus(status).name}", LogLevel.INFO.value)

                    else:
                        log_msg(f"Статус запроса не 200 → Статус: {resp.status}. Response: {res}", LogLevel.ERORR.value)
                        status = RedashAPI.JobStatus.CANCELLED.value
                        query_result_id = 0
                        break

            except Exception as e:
                log_msg(f"Ошибка при проверке статуса job: {e}", LogLevel.ERORR.value)
                status = RedashAPI.JobStatus.CANCELLED.value
                query_result_id = 0
                break

            await asyncio.sleep(5)

        return status, query_result_id

    @log_call
    async def get_result_job(self, query_result_id : int) -> dict:
        """
        получает результат работы Job'а и возвращает его dict 

        Args:
            query_result_id(int): id результата query
        Returns:
            dict: json ответ
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with RedashClient()`")

        url = f"{RedashAPI.Endpoints.BASE_URL}{RedashAPI.Endpoints.GET_RESULT_JOB_ENDPOINT.format(query_result_id=query_result_id)}"
        
        async with self.cl_session.get(url=url, headers=self.AUTH_HEADER) as resp:
            res = await resp.json() # парсим ответ
            if resp.status == 200:
                log_msg("Ответ от сервера 200", LogLevel.SUCCESS.value)
                return res
            else:
                log_msg("Ответ от сервера не 200", LogLevel.WARN.value)
                return res

    @overload
    async def start_job(self, body : dict, url : str, query : int) -> str: # если указывается URL - query обязателен
        ...
    @overload
    async def start_job(self, body : dict, url : str = RedashAPI.Endpoints.START_SQL_JOB, query : int | None = None) -> str: # если не указывается URL - query не обязателен
        ...
    @log_call
    async def start_job(self, body: dict, url: str = RedashAPI.Endpoints.START_SQL_JOB, query: int | None = None) -> str:
        """
        Запускает Job по запросу. Можно запустить либо свой SQL запрос либо уже существующий по query 

        Args:
            body(dict): Сам запрос. Может содержать параметры для существующего запроса или SQL запрос
            url(str): Endpoint для запроса. Если не указан то будет подставляться endpoint для SQL. Если указывается то RedashAPI.Endpoints.START_JOB_ENDPOINT и обязательно указывается query 
            query (int|None): Номер существующего query 
        Returns:
            str: job_id по которму можно отслеживать статус работы
                - Если запрошел не корректно - вернется "null"
        """
        if not self.cl_session:
            raise RuntimeError("Сессия не инициализирована. Используй `async with RedashClient()`")
        
        # Форматируем URL если это endpoint для существующего query
        if url == RedashAPI.Endpoints.START_JOB_ENDPOINT and query is not None:
            url = url.format(query=query)
        elif url == RedashAPI.Endpoints.START_JOB_ENDPOINT and query is None:
            raise ValueError("Для START_JOB_ENDPOINT необходимо указать query")
        
        # Собираем полный URL
        full_url = f"{RedashAPI.Endpoints.BASE_URL}{url}"
        
        async with self.cl_session.post(url=full_url, headers=self.AUTH_HEADER, json=body) as resp:
            res = await resp.json()
            
            if resp.status == 200:
                log_msg(f"Job успешно запущен", LogLevel.SUCCESS.value)
                job = res.get('job') or {}
                job_id = job.get('id') or "null"
                return job_id
            else:
                mes = res.get('message')
                log_msg(f"Сервер ответил не 200 на запрос запуска Job'а. Сообщение: {mes}", LogLevel.WARN.value)
                job_id = "null"
                return job_id

    # ---------------------------------------------------------------------------
    @log_call
    async def get_schedules_by_mp(self, marketplace : Marketplace) -> dict[str, int]:
        """
        Запускает query дашборда Redash и возвращает количество расписаной для МП в каждом РК

        Args:
            marketplace(Marketplace): Маркетплейс по РК которого будет выполнен поиск расписаний
        Returns:
            dict: Количество расписаний для каждого региона МП где РК - ключ, а количество расписаний - значение
        """
        payload = RedashAPI.QueryBody.SCHEDULES_QUERY.copy()
        payload["parameters"]["Маркетплейс"] = marketplace.name

        results = []
        for region in marketplace.regions:
            payload["РК"] = region
            job_id = await self.start_job(body=payload, url=RedashAPI.Endpoints.START_JOB_ENDPOINT, query=886)
            if job_id != "null":
                status, result_id = await self.check_status_job(job_id)
                if result_id != 0:
                    log_msg(f"Redash job успешно отработал. Последний статус: {status}", LogLevel.SUCCESS.value)
                    results.append(await self.get_result_job(result_id))
                else:
                    log_msg(f"Redash job не отработал. Последний статус: {status}", LogLevel.ERORR.value)
        
        schedules_by_rk = {}
        for result in results:
            data = result.get("data") or {}
            rows = data.get("rows") or []
            
            schedules_count = 0
            for row in rows:
                if row.get("status_name", "") == "Расписание сформировано":
                    num = row.get("num") or 0
                    schedules_count += num if isinstance(num, int) else 0
                
                rk = row.get("rk")
                
                log_msg(f"РК: {rk}, Количество расписаний: {schedules_count}", LogLevel.INFO.value)
                schedules_by_rk[rk] = schedules_count

        return schedules_by_rk

    # ---------------------------------------------------------------------------

    def _filter(self, raw_info_about_problem_regions: list[dict]) -> list[dict]:
        """
        фильтрует оставляя только те dict где динамика отрицательная (то есть -%)
        """
        info_about_problem_regions = []
        for item in raw_info_about_problem_regions:
            text = item.get("change") or ""
            cleaned = ''.join(c for c in text if c in '+-.0123456789')

            if float(cleaned) < 0:
                info_about_problem_regions.append(item)

        return info_about_problem_regions


    @log_call
    async def _parse_info_about_problem_regions(self, data: dict) -> dict:
        """
        Из ответа вытягивает Кол-во заказов, их динамику и регион.
        PS: эту хуйню писал GPT так что я хз как оно работает. Тут используются регулярки а я в них не шарю вообще. 

        Args:
            data(dict): Ответ с дашборда который будет парсится
        Returns:
            dict: Json с количеством заказов, РК и динамикой
        """
        # Достаем название региона
        region_html = data.get("organization_name", "")
        region = re.sub(r'<[^>]+>', '', region_html).strip()
        
        # Достаем значение и изменение из "Кол-во заказов"
        orders_html = data.get("Кол-во заказов", "")
        clean_text = re.sub(r'<[^>]+>', '', orders_html)
        
        # Ищем значение
        value_match = re.search(r':\s*(\d+)', clean_text)
        value = float(value_match.group(1)) if value_match else None
        
        # Ищем изменение
        change_match = re.search(r'\(([^)]+)\)', clean_text)
        change = change_match.group(1) if change_match else None
        
        return {
            "region": region,
            "value": value,
            "change": change
        }

    @log_call
    async def get_info_about_problem_regions(self, marketplace : Marketplace) -> list[dict]:
        """        
        Запускает query для получения инфы о количестве заказов в каждом РК и их динамике п омаркетплейсу.
        Внутри дополнительно вызывается метод для парсинга ответа от Redash так как он возвращает json с html

        Args:
            markeplace(Marketplace): Маркетплейс у которого будет собираться статистика по РК
        Returns:
            list[dict]: Список данных по РК о заказах
        """
        results = []
        
        payload = RedashAPI.QueryBody.PROBLEM_RK_QUERY.copy()
        payload["parameters"]["marketplace_name"] = marketplace.name

        job_id = await self.start_job(body=payload, url=RedashAPI.Endpoints.START_JOB_ENDPOINT, query=9021)
        if job_id != "null":
            status, result_id = await self.check_status_job(job_id)
            if result_id != 0:
                log_msg(f"Redash job успешно отработал. Последний статус: {status}", LogLevel.SUCCESS.value)
                result = json.loads(json.dumps(await self.get_result_job(result_id)))# докодируем ответ потому что он приходит в формате unicode последовательности (типо так → "\u041a\u043e\u043b-\u0432\u043e \u0437\u0430\u043a\u0430\u0437\u043e\u0432")
                query_result = result.get("query_result") or {}
                data = query_result.get("data") or {}
                rows = data.get("rows") or []

                for row in rows:
                    results.append(await self._parse_info_about_problem_regions(row))

            else:
                log_msg(f"Redash job не отработал. Последний статус: {status}", LogLevel.ERORR.value)
        
        return self._filter(results) # что бы оставить только записи где -%

    # ---------------------------------------------------------------------------

    @log_call
    async def get_info_about_history(self, marketplace : Marketplace) -> dict:
        """
        Получает истроческие данные количества заказов за текущий день недели по МП (то есть если сегодня вторник - выдаст данные за все вторники за 30 дней)

        Args:
            marketplace(Marketplace): Маркетплейс для которого будет собираться статистика.
        Returns:
            dict: Данные по заказам за каждый (текущий) день недели за 30 дней, где дата - ключ, количество заказов - значение
        """
        history = {}
        
        payload = RedashAPI.QueryBody.HISTORY_QUERY.copy()
        payload["parameters"]["marketplace_name"] = marketplace.name

        job_id = await self.start_job(body=payload, url=RedashAPI.Endpoints.START_JOB_ENDPOINT, query=9018)
        if job_id != "null":
            status, result_id = await self.check_status_job(job_id)
            if result_id != 0:
                log_msg(f"Redash job успешно отработал. Последний статус: {status}", LogLevel.SUCCESS.value)
                result = await self.get_result_job(result_id)
                query_result = result.get("query_result") or {}
                data = query_result.get("data") or {}
                rows = data.get("rows") or []
                rows.reverse()

                history = {}
                target_date = datetime.datetime.now().strftime('%Y-%m-%d')

                for row in rows:
                    if target_date == (datetime.datetime.strptime(row.get("data"), "%Y-%m-%d").strftime('%Y-%m-%d')):
                        count_orders = row.get("Кол-во заказов")
                        history[datetime.datetime.strptime(row.get("data"), "%Y-%m-%d")] = count_orders

                        target_date = (datetime.datetime.strptime(row.get("data"), "%Y-%m-%d") - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            else:
                log_msg(f"Redash job не отработал. Последний статус: {status}", LogLevel.ERORR.value)
                history = {}
        
        return history

    # ---------------------------------------------------------------------------

    @log_call
    async def get_info_discrepancy_stors_by_regions(self, marketplace : Marketplace) -> dict:
        """
        Прокидывает SQL запрос через redash на получение количества ТВЗ в 1С и ECOM по всем РК маркетплейса.

        Args:
            marketplace(Marketplace): Маркетплейс для которого будет происходить поиск
        Returns:
            dict: список в котором РК - ключ, а количество ТВЗ в еком\\1с и их схождение это список
                - "region" : {
                        "one_s" : one_s_count,
                        "ecom" : ecom_count,
                        "convergence" : convergence
                    }
        """
        payload = {
            "query": RedashAPI.QueryBody.SQL_DISCREPANCY_STORS_BY_REGIONS.format(mp_id=marketplace.id),
            "data_source_id": 24,
            "max_age" : 0
        }
        job_id = await self.start_job(payload)
        
        if job_id != "null":
            status, result_id = await self.check_status_job(job_id)
            if result_id != 0:
                log_msg(f"Redash job успешно отработал. Последний статус: {status}", LogLevel.SUCCESS.value)
                result = json.loads(json.dumps(await self.get_result_job(result_id))) # декодируем ответ потому что он приходит в формате unicode последовательности (типо так → "\u041a\u043e\u043b-\u0432\u043e \u0437\u0430\u043a\u0430\u0437\u043e\u0432")
                query_result = result.get("query_result")
                data = query_result.get("data")
                rows = data.get("rows")

                result = {}
                for row in rows:
                    region = row.get("РК") or "null"
                    one_s_count = row.get("1С") or 0
                    ecom_count = row.get("Ecom") or 0
                    convergence = row.get("Доля схождений") or 100.0

                    result[region] = {
                        "one_s" : one_s_count,
                        "ecom" : ecom_count,
                        "convergence" : convergence
                    }
            else:
                log_msg(f"Redash job не отработал. Последний статус: {status}", LogLevel.ERORR.value)
                result = {}
        return result
        
            
