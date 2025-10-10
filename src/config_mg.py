import json
from src.loger import log_call, log_msg, LogLevel
from src.models import Marketplace

class Config_mg:

    @log_call
    def read_config(self, file_path: str = "marcetplaces_config.jsonl") -> list[Marketplace]:
        """
        Читает jsonl файл и возвращает список валидированных Marketplace объектов

        Args:
            file_path(str): Путь до файла конфига
        Returns:
            list[src.models.Marketplace]: Список маркетплейсов вытащеных из конгфига
        """
        marketplaces = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:  # пропускаем пустые строки
                    continue

                try:
                    data = json.loads(line)
                    marketplace = Marketplace(**data)
                    marketplaces.append(marketplace)
                except json.JSONDecodeError as e:
                    log_msg(f"Ошибка JSON в строке {line_number}: {e}", LogLevel.ERORR.value)
                except Exception as e:
                    log_msg(f"Ошибка валидации в строке {line_number}: {e}", LogLevel.ERORR.value)
        
        return marketplaces
    
    @log_call
    def add_marketplace_to_config(self, marketplace_data: dict, file_path: str = "marcetplaces_config.jsonl") -> bool:
        """
        Добавляет новый маркетплейс в конфиг файл (JSONL)
        
        Args:
            marketplace_data: Данные маркетплейса в виде словаря
            file_path: Путь к файлу конфигурации
        
        Returns:
            bool: True если успешно добавлено, False если ошибка
        """
        try:
            # Валидируем данные через Pydantic модель
            marketplace = Marketplace(**marketplace_data)
            
            # Преобразуем обратно в dict для сохранения, преобразуя Enum в строки
            data_to_save = marketplace.model_dump()
            
            # Преобразуем Region и Env объекты в строки для JSON сериализации
            data_to_save["regions"] = [region.name for region in data_to_save["regions"]]
            data_to_save["env"] = data_to_save["env"].value
            
            # Добавляем в конец файла как новую строку JSON
            with open(file_path, 'a', encoding='utf-8') as file:
                json_line = json.dumps(data_to_save, ensure_ascii=False)
                file.write(json_line + '\n')
            
            log_msg(f"Маркетплейс '{marketplace.name}' успешно добавлен в конфиг", LogLevel.SUCCESS.value)
            return True
            
        except Exception as e:
            log_msg(f"Ошибка при добавлении маркетплейса: {e}", LogLevel.ERORR.value)
            return False

    @log_call
    async def create_marketplace_interactively(self, file_path: str = "marcetplaces_config.jsonl") -> bool:
        """
        Интерактивное создание и добавление маркетплейса через консоль

        Args:
            file_path(str): Путь по которому лежит файл .jsonl конфиг
        Returns:
            bool: True если конфиг добавлен, False - если не добавлен
        """
        log_msg("Создание нового маркетплейса:", LogLevel.INFO.value)
        
        try:
            marketplace_data = {
                "active": input("Варианты: true/false\nАктивен: ").lower() == 'true',
                "id": int(input("ID: ")),
                "guid": input("GUID: "),
                "name": input("Название (должно быть как в БД): "),
                "elk_name": input("Имя для ELK запросов: "),
                "regions": input("Доступные регионы: MSK / YRS / BRN / SPB / VLG / VRN / KZN / KRN(краснодар) / HBR / IRK / KRS(красноярск) / EKB / NSK / SAM\nРегионы МП (через пробел): ").upper().split(' '),
                "env": input("Варианты: LTS/LATEST/POLZA\nОкружение: ").upper()
            }
            
            return self.add_marketplace_to_config(marketplace_data, file_path)
            
        except Exception as e:
            log_msg(f"Ошибка ввода: {e}", LogLevel.ERORR.value)
            return False
        
    

