from src.loger import log_call, log_msg, LogLevel
from src.models import Marketplace

class Menu:

    def __init__(self) -> None:
        ...
    def _show_menu(self, menu : list) -> int:
        """
        Отображает меню и ожидает ввода индекса пункта меню
        """
        print("Меню:")
        i = 0
        for item in menu:
            print(f"{i} - {item}")
            i += 1

        try:
            selected = int(input(": "))
            if selected > i:
                log_msg("Не корректный выбор, выбраного пункта не существует")
                self._show_menu(menu)

        except Exception as e:
            log_msg(f"Не корректный выбор. Ошибка: {e}")

        return selected

    def _get_action_in_menu(self, selected_index:int, actions: dict):
        """
        Вызывает действие в зависимости от выбора пользователя (возвращает (по сути вызывает) лямбду функцию из словаря actions)
        """
        action = actions.get(selected_index) or (lambda: None)
        return action()
        
    def menu(self, menu: list, actions: dict):
        """
        Отображает меню и вызывает действие в зависимости от выбора пользователя

        Args:
            menu (list): Список пунктов меню для отображения
            actions (dict): Словарь, где ключ - индекс пункта меню, значение - ЛЯМБДА функция для вызова
        Returns:
            None (вызов функции действия)
        """
        select = self._show_menu(menu)
        return self._get_action_in_menu(select, actions)
