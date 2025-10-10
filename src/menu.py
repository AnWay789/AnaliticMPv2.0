from src.loger import log_call, log_msg, LogLevel
from src.models import Marketplace

class Menu:

    def __init__(self, menu : list, actions : dict) -> None:
        self.MENU = menu
        self.ACTIONS = actions

    def show_main_menu(self) -> int:
        print("Меню:")
        i = 0
        for item in self.MENU:
            print(f"{i} - {item}")
            i += 1

        try:
            selected = int(input(": "))
            if selected > i:
                log_msg("Не корректный выбор, выбраного пункта не существует")
                self.main_menu()

        except Exception as e:
            log_msg(f"Не корректный выбор. Ошибка: {e}")
            self.main_menu()

        return selected

    def get_action_in_main_menu(self, selected_index:int):
        action = self.ACTIONS.get(selected_index) or (lambda: log_msg("Не корректный выбор, выбраного пункта не существует"))
        return action()

    def change_marketplaces(self, marketplaces: list[Marketplace]) -> Marketplace:
        changed = int(input("Выберете маркетплейс из списка выше (введите индекс)\n :"))
        marketplace = marketplaces[changed]
        return marketplace

    def show_marketplaces(self, marketplaces: list[Marketplace]):
        i = 0
        for marketplace in marketplaces:
            print(f"{i} - {marketplace.name}")
            i += 1
        
    def main_menu(self):
        select = self.show_main_menu()
        self.get_action_in_main_menu(select)
