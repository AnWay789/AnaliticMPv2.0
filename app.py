import asyncio
from src.grafana.grafana_api import GrafanaAPI

from src.loger import log_call, log_msg, LogLevel
from src.models import Env, Marketplace

from src.menu import Menu
from src.config_mg import Config_mg
from src.grafana.grafana import GrafanaClient
from src.redash.redash import RedashClient
from src.config_mg import Config_mg

class App:
    
    def __init__(self) -> None:
        self.MAIN_MENU = [
            "-→ Запустить аналитику", # пункт меню 0
            "↓ Добавить маркетплейс", # пункт меню 1
        ]
        self.MAIN_ACTIONS = {
            0 : lambda: asyncio.run(self._start_analitic()), # эти функции будут вызываться при выборе пункта меню 0
            1 : lambda: self.cfg.create_marketplace_interactively(), # эти функции будут вызываться при выборе пункта меню 1
        }

        self.MENU = Menu()
        self.cfg = Config_mg()

    def start_app(self):
        self.MENU.menu(self.MAIN_MENU, self.MAIN_ACTIONS) # главное меню




    async def _start_analitic(self) -> None:
        marketplaces = self.cfg.read_config()
        
        # генерируем меню (список) для выбора маркетплейса
        marketplaces_menu = []
        for mp in marketplaces:
            marketplaces_menu.append(f"{mp.name} ({mp.env.value})")
        marketplaces_menu.append("← Назад") # добавляем пункт возврата в главное меню

        # генерируем действия для каждого МП из меню
        actions = {}
        for i, mp in enumerate(marketplaces): # тут создаем динамическое меню для выбора маркетплейса
            actions[i] = lambda: asyncio.run(self._do_analitic(mp))
        actions[(len(marketplaces))] = lambda: self.start_app() # возврат в главное меню

        self.MENU.menu(marketplaces_menu, actions)
    
    @log_call
    async def _do_analitic(self, marketplace: Marketplace) -> None:
        grafana = GrafanaClient()
        redash = RedashClient()
        
        # нужен для получения информации о обменах по заказам, остаткам и ценам
        req_map = [
            {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_ORDERS_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_ORDERS_LUCENE
            },
            {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_STOCKS_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_STOCKS_LUCENE
            },
            {
            Env.LTS.value : GrafanaAPI.LuceneRequestes.ELK_LTS_PRICES_LUCENE,
            Env.LATEST.value : GrafanaAPI.LuceneRequestes.ELK_LATEST_PRICES_LUCENE
            }
        ]

        # --------------------------------------------- GRAFANA ↓
        async with grafana as g:
            stors = await g.get_count_stors(marketplace)

            if isinstance(res := await g.get_status_cache(marketplace), tuple):
                cache, details = res
            else:
                cache = res
                details = {}

            exchanges = []
            for req in req_map:
                hits, time = await g.get_value_exchanges_by_req(marketplace, req)
                exchanges.append((hits, time))

        # ↑ GRAFANA --------------------------------------------- REDASH ↓
        async with redash as r:
            history = await r.get_info_about_history(marketplace)
            problem_regions = await r.get_info_about_problem_regions(marketplace)
            schedules_by_region = await r.get_schedules_by_mp(marketplace)
            discrepancy_stors = await r.get_info_discrepancy_stors_by_regions(marketplace)

        self._create_report(
            stors = stors,
            cache = cache,
            details = details,
            orders = exchanges[0][0], time_orders = exchanges[0][1],
            stocks = exchanges[1][0], time_stocks = exchanges[1][1],
            prices = exchanges[2][0], time_prices = exchanges[2][1],
            history = history,
            problem_regions = problem_regions,
            discrepancy_stors = discrepancy_stors)

    @log_call
    def _create_report(self, stors : dict[str, str],
                  cache : str,
                  details: str | dict,
                  orders: int | str, time_orders: int,
                  stocks: int | str, time_stocks: int,
                  prices: int | str, time_prices: int,
                  history: dict,
                  problem_regions: list[dict],
                  discrepancy_stors: dict,
                  schedules_by_region: dict = {}) -> None:
        print(f"ТВЗ: {stors}\n\nКэш: {cache}\nДетали: {details}\n\nЗаказы: {orders}\nВременной отрезок: {time_orders}мин\n\nОстатки: {stocks}\nВременной отрезок: {time_stocks}мин\n\nЦены: {prices}\nВременной отрезок: {time_prices}мин\n\nИсторические данные: {history}\n\nПроблемные РК: {problem_regions}\n\nРасхождения ТВЗ:{discrepancy_stors}")

# if __name__ == "__main__":
#     try: 
#         start()
#     except Exception as e:
#         log_msg(f"Ошибка в main: {e}", LogLevel.ERORR.value)
#     finally:
#         print("\n\n\n")
#         start()
