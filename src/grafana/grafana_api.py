from enum import Enum

class GrafanaAPI():
    
    class Endpoints():

        BASE_URL = "https://grafana02.puls.ru"

        AUTH_ENDPONT = "/login"
        ELK_MULTI_SEARCH_ENDPOINT = "/api/datasources/proxy/{source_id}/_msearch"
        ELK_SEARCH_ENDPOINT = "/api/datasources/proxy/{source_id}/_search"
        QUERY_ENDPOINT = "/api/ds/query"

    class Sources():
        LATEST_POSTGRES_DATASOURCE = {"type" : "postgres", "uid" : "LRv7BwRNk"}
        LTS_POSTGRES_DATASOURCE = {"type" : "postgres", "uid" : "NZ6mrUSSz"}
        POLZA_POSTGRES_DATASOURCE = {"type" : "postgres", "uid" : "bgCdmzHIk"}

        DHW_CLICKHOUSE_DATASOURCE = {"type" : "grafana-clickhouse-datasource", "uid" : "z4ICaIsIz"}

        LTS_VICTORIA_METRICS_DATASOURCE = {"type" : "prometheus", "uid" : "hyUVBGfVk"} # Существует потому что celary для LTS тянется отсюда
        LATEST_PROMETHEUS_DATASOURCE = {"type" : "prometheus", "uid" : "BetMIQSIz"}
        POLZA_PROMETHEUS_DATASOURCE = {"type" : "prometheus", "uid" : "BetMIQSIz"}
        BFF_PROMETHEUS_DATASOURCE = {"type" : "prometheus", "uid" : "BetMIQSIz"}

        ELK_LTS_SOURCE = "apm-*prod-ecom*"
        ELK_LTS_SOURCE_ID = 17
        ELK_LATEST_SOURCE = "apm-*prod-latest-ecom*"
        ELK_LATEST_SOURCE_ID = 71

    class SQLRequsts():
        # Эти запросы я взял тупо с дашборда, поэтому и разбил на разные окружения (возможно можно составить и без них, но я хз как)
        # Что бы увидеть в нормальном виде запрос - используй https://codebeautify.org/sqlformatter
        LTS_STORS_SQL = "select uniqExact(`after.marketplace_store_id`) from (select * from `default`.`ecom-lts.debezium.cdc.public.delivery_organizationaddress` FINAL) oa inner join (select * from `default`.`ecom-lts.debezium.cdc.public.delivery_marketplacestore` FINAL) ms on oa.`after.marketplace_store_id` = ms.`after.id` WHERE ms.`after.is_active` and `after.organization_id` = {org_id} and `after.marketplace_id` = {mp_id}"
        LATEST_STORS_SQL = "select uniqExact(`after.marketplace_store_id`) from (select * from `default`.`ecomlatest.debezium.cdc.public.delivery_organizationaddress` FINAL) oa inner join (select * from `default`.`ecomlatest.debezium.cdc.public.delivery_marketplacestore` FINAL) ms on oa.`after.marketplace_store_id` = ms.`after.id` WHERE ms.`after.is_active` and `after.organization_id` = {org_id} and `after.marketplace_id` = {mp_id}"
        POLZA_STORS_SQL = "select uniqExact(`after.marketplace_store_id`) from (select * from `default`.`ecompolza.debezium.cdc.public.delivery_organizationaddress` FINAL) oa inner join (select * from `default`.`ecompolza.debezium.cdc.public.delivery_marketplacestore` FINAL) ms on oa.`after.marketplace_store_id` = ms.`after.id` WHERE ms.`after.is_active` and `after.organization_id` = {org_id} and `after.marketplace_id` = {mp_id}"

        # Этот запрос я составил сам. Он выбирает по имени маркетплейса и в запросе не используется конкретное окружение, то есть его использовать нужно совместно с LTS_POSTGRES, LATEST_POSTGRES или POLZA_POSTGRES. Этот статус возвращает таблицу с количеством остатков в БД, в КЭШе и их процентное РАСХОЖДЕНИЕ
        DITAILS_CACHE_SQL = "SELECT DISTINCT ON (s.org_name, mm.name, s.marketplace_guid) s.org_name, s.db_count, s.cache_count, s.percent FROM statistic_nonzerostockmetric s INNER JOIN marketplace_marketplace mm ON mm.guid = s.marketplace_guid::uuid and mm.name = {mp_name} WHERE s.actual = true ORDER BY s.org_name, s.marketplace_guid;"
        # Этот запрос с дашборда (я его совсем каплю подредактировал что бы выводился только статус), он возвращает ТОЛЬКО статус кэша для МП
        CACHE_SQL = "select status from statistic_nonzerostockmetricstatus where actual=True and marketplace_guid={mp_guid};"
                     
    class PQLRequstes():
        LTS_CELARY_PQL = "celery_queue_length{namespace=s~\"master-ecommerce\"}"
        LATEST_CELARY_PQL = "celery_queue_length{namespace=~\"ecom-latest-prod\"}"
        POLZA_CELARY_PQL = "celery_queue_length{namespace=~\"ecommerce-prod\"}"
        BFF_CELARY_PQL = "celery_queue_length{namespace=~\"bff-prod\"}"

    class LuceneRequestes():
        # Эти запросы напрямую с Grafana борда
        ELK_LTS_ORDERS_LUCENE = "processor.event:\"transaction\" AND service.environment: \"prod\" AND (url.path: \"/v1.0/orders\" OR transaction.name: *YandexOrderAcceptView* OR (transaction.name : *SbermmOrderNewView*) OR (transaction.name : *BaseImportOrderService*) OR (transaction.name: *OrderView_for_garmoniya*)) AND user.name: {mp_name}"# type: ignore ← линтер/IDE ругается что "\/" - это не поддерживаемая escape последовательность. Добавил эти коменты что бы не ругалось. Эти последовательности - части запроса в ELK. Их менять нельзя.
        ELK_LATEST_ORDERS_LUCENE = "processor.event:\"transaction\" AND service.environment: \"selectel-prod-latest\" AND (url.path: \"/v1.0/orders\" OR transaction.name: *YandexOrderAcceptView* OR (transaction.name : *SbermmOrderNewView*) OR (transaction.name : *BaseImportOrderService*) OR (transaction.name: \"GET https://marketplace-api.wildberries.ru/api/v3/orders/new\") OR (transaction.name: \"GET https://marketplace-api.wildberries.ru/api/v3/dbs/orders/new\")) AND user.name: {mp_name}"# type: ignore

        ELK_LTS_STOCKS_LUCENE = "((processor.event:\"transaction\" AND service.environment: \"prod\" AND (transaction.name:/.*stock_changes.*/ OR transaction.name: *api\/products\/stocks*  OR transaction.name:*offers\/stocks* )) OR (transaction.name: /.*GET.*Stock.*/ AND http.response.status_code: 200) OR (transaction.name:/.*seller.*/ AND transaction.name:/.*stocks.*/) OR (transaction.name: *api.aptekamos.ru\/Price\/WPrice\/WimportPrices*)) AND service.name: (\"ecom\" OR \"ecom-polza\") AND user.name: {mp_name}"# type: ignore
        ELK_LATEST_STOCKS_LUCENE = "((processor.event:\"transaction\" AND service.environment: \"selectel-prod-latest\" AND (transaction.name:/.*stock_changes.*/ OR transaction.name: *api\/products\/stocks*  OR transaction.name:*offers\/stocks* )) OR (transaction.name: /.*GET.*Stock.*/ AND http.response.status_code: 200) OR (transaction.name:/.*seller.*/ AND transaction.name:/.*stocks.*/) OR (transaction.name: *api.aptekamos.ru\/Price\/WPrice\/WimportPrices*) OR (transaction.name: *\/api\/v3\/stocks\/*)) AND service.name: (\"ecom\" OR \"ecom-polza\") AND user.name: {mp_name}" # type: ignore

        ELK_LTS_PRICES_LUCENE = "((processor.event:\"transaction\" AND transaction.name: /POST.*price.*/ AND NOT transaction.name: /.*ECommerceInternalAPI.*/) OR (transaction.name: /.*GET.*Stock.*/ AND http.response.status_code: 200 AND NOT user.name: sozvezdie)) AND user.name: {mp_name}"
        ELK_LATEST_PRICES_LUCENE = "((processor.event:\"transaction\" AND transaction.name: /POST.*price.*/ AND NOT transaction.name: /.*ECommerceInternalAPI.*/) OR (transaction.name: /.*GET.*Stock.*/ AND http.response.status_code: 200 AND NOT user.name: sozvezdie) OR (transaction.name: *\/api\/v2\/upload\/task*)) AND user.name: {mp_name}"# type: ignore

