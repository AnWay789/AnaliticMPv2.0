import asyncio
from src.grafana.grafana import GrafanaClient
from src.grafana.grafana_api import GrafanaAPI
from src.redash.redash import RedashClient
from src.utils import Utils
from src.loger import log_call, log_msg, LogLevel
from src.models import Env, Marketplace

MENU = [
        "Запустить аналитику",
        "Добавить маркетплейс"
    ]


def analitic():
    marketplaces = load_config()
    show_marketplaces(marketplaces)
    marketplace = change_marketplaces(marketplaces)

    asyncio.run(start_analitic(marketplace))

def _create_report(stors : dict[str, str],
                  cache : str,
                  details: str | dict,
                  orders: int | str, time_orders: int,
                  stocks: int | str, time_stocks: int,
                  prices: int | str, time_prices: int,
                  history: dict,
                  problem_regions: list[dict],
                  discrepancy_stors: dict):
    print(f"ТВЗ: {stors}\n\nКэш: {cache}\nДетали: {details}\n\nЗаказы: {orders}\nВременной отрезок: {time_orders}мин\n\nОстатки: {stocks}\nВременной отрезок: {time_stocks}мин\n\nЦены: {prices}\nВременной отрезок: {time_prices}мин\n\nИсторические данные: {history}\n\nПроблемные РК: {problem_regions}\n\nРасхождения ТВЗ:{discrepancy_stors}")



async def start_analitic(marketplace):
    # --------------------------------------------- GRAFANA ↓
    async with GrafanaClient() as grafana_client:
        stors = await grafana_client.get_count_stors(marketplace)
        await asyncio.sleep(5)
        if isinstance(res := await grafana_client.get_status_cache(marketplace), tuple):
            cache, details = res
        else:
            cache = res
            details = {}

        elk_orders_req_map = {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_ORDERS_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_ORDERS_LUCENE
        }
        elk_stocks_req_map = {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_STOCKS_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_STOCKS_LUCENE
        }
        elk_prices_req_map = {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_PRICES_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_PRICES_LUCENE
        }
        orders, time_orders = await grafana_client.get_value_exchanges_by_req(marketplace, elk_orders_req_map)
        stocks, time_stocks = await grafana_client.get_value_exchanges_by_req(marketplace, elk_stocks_req_map)
        prices, time_prices = await grafana_client.get_value_exchanges_by_req(marketplace, elk_prices_req_map)

    # ↑ GRAFANA --------------------------------------------- REDASH ↓
    async with RedashClient() as redash_client:
        history = await redash_client.get_info_about_history(marketplace)
        problem_regions = await redash_client.get_info_about_problem_regions(marketplace)
        
        discrepancy_stors = await redash_client.get_info_discrepancy_stors_by_regions(marketplace)

    _create_report(
        stors=stors,
        cache=cache, details=details,
        orders=orders, time_orders=time_orders,
        stocks=stocks, time_stocks=time_stocks,
        prices=prices, time_prices=time_prices,
        history=history,
        problem_regions=problem_regions,
        discrepancy_stors=discrepancy_stors
    )


def add_marketplace():
    is_add = Utils.create_marketplace_interactively()

    if is_add:
        log_msg("Маркетплейс добавлен", LogLevel.SUCCESS.value)
    else:
        log_msg("Маркетплейс не добавлен", LogLevel.ERORR.value)


def main_menu() -> int:
    print("Меню:")
    i = 0
    for item in MENU:
        print(f"{i} - {item}")
        i += 1

    try:
        selected = int(input(": "))
        if selected > i:
            log_msg("Не корректный выбор, выбраного пункта не существует")
            main_menu()

    except Exception as e:
        log_msg(f"Не корректный выбор. Ошибка: {e}")
        main_menu()

    return selected

def change_marketplaces(marketplaces: list[Marketplace]) -> Marketplace:
    changed = int(input("Выберете маркетплейс из списка выше (введите индекс): "))
    marketplace = marketplaces[changed]
    return marketplace

def show_marketplaces(marketplaces: list[Marketplace]):
    i = 0
    for marketplace in marketplaces:
        print(f"{i} - {marketplace.name}")
        i += 1

def load_config() -> list[Marketplace]:
    marketplaces = Utils.read_config()
    return marketplaces


if __name__ == "__main__":
    selected = main_menu()

    if selected == 0:
        marketplaces = load_config()
        show_marketplaces(marketplaces)
        changed_marketplaces = change_marketplaces(marketplaces)
        print(changed_marketplaces)
        asyncio.run(start_analitic(changed_marketplaces))
    elif selected == 1:
        add_marketplace()
        main_menu()
