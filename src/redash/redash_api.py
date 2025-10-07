from enum import Enum
import datetime
class RedashAPI():
    
    class Endpoints:
        BASE_URL = "https://redash.polza.ru"

        START_JOB_ENDPOINT = "/api/queries/{query}/results"
        GET_STATUS_JOB_ENDPOINT = "/api/jobs/"
        GET_RESULT_JOB_ENDPOINT = "/api/query_results/{query_result_id}"

        START_SQL_JOB = "/api/query_results"
    
    class JobStatus(Enum):
        PENDING = 1
        STARTED = 2
        SUCCESS = 3
        FAILURE = 4
        CANCELLED = 5
 
    class QueryBody:
        SCHEDULES_QUERY = {"id":8862,"parameters":{"Маркетплейс":"{mp_name}","РК":"{reg_name}","Регион":["Bce регионы"]},"apply_auto_limit":False,"max_age":0}
        PROBLEM_RK_QUERY = {"id":9021,"parameters":{"marketplace_name":"{mp_name}"},"apply_auto_limit":False,"max_age":0}
        HISTORY_QUERY = {"id":9018,"parameters":{"Период":{"start":f"{(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')}","end":f"{datetime.datetime.now().strftime('%Y-%m-%d')}"},"Тип отрезка":"day","marketplace_name":"{mp_name}"},"apply_auto_limit":False,"max_age":0}
        SQL_DISCREPANCY_STORS_BY_REGIONS = "with b as ( select marketplace_id, rk_id, rk, addressguid, tvz_1c, tvz_ec from cached_query_8437 where marketplace_id = {mp_id} ) select 0 as \"РК id\", 'Все РК' as \"РК\", count(tvz_1c) as \"1С\", count(tvz_ec) as \"Ecom\", sum(case when tvz_1c > 0 and tvz_ec is null then 1 else 0 end) || ' / ' || sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end) as \"Отсутствуют/Лишние (Ecom-1С)\", coalesce(round((sum(case when tvz_1c = tvz_ec then 1 else 0 end) - sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end)) * 100.0 / count(tvz_1c), 2), 0.00) as \"Доля схождений\", datetime('now','+3 hour') as dt from b union select rk_id, rk, count(tvz_1c) as tvz_1c, count(tvz_ec) as tvz_ec, sum(case when tvz_1c > 0 and tvz_ec is null then 1 else 0 end) || ' / ' || sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end) as lc_ec, coalesce(round((sum(case when tvz_1c = tvz_ec then 1 else 0 end) - sum(case when tvz_1c is null and tvz_ec > 0 then 1 else 0 end)) * 100.0 / count(tvz_1c), 2), 0.00) as lc_ec_p, datetime('now','+3 hour') as dt from b where rk is not null and rk <> 'Нет инфо' group by rk_id, rk"
        
