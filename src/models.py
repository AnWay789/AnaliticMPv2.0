from pydantic import BaseModel, field_validator
from src.regions import Region
from enum import Enum

class Env(Enum):
    LTS = "LTS"
    LATEST = "LATEST"
    POLZA = "POLZA"

class Marketplace(BaseModel):
    active : bool
    id : int
    guid : str
    name : str # Имя должно быть как в БД
    elk_name : str
    regions : list[Region]
    env : Env 

    @field_validator('regions', mode='before')
    @classmethod
    def validate_regions(cls, v):
        """Преобразует строки в объекты Region"""
        if isinstance(v, list):
            validated_regions = []
            for item in v:
                if isinstance(item, str):
                    # Ищем соответствующий Enum по имени
                    try:
                        region_enum = Region[item]  # Region['MSK'] -> Region.MSK
                        validated_regions.append(region_enum)
                    except KeyError:
                        raise ValueError(f"Неизвестный регион: {item}")
                elif isinstance(item, Region):
                    validated_regions.append(item)
                else:
                    raise ValueError(f"Неподдерживаемый тип региона: {type(item)}")
            return validated_regions
        return v

    @field_validator('env', mode='before')
    @classmethod
    def validate_env(cls, v):
        """Преобразует строку в Enum Env"""
        if isinstance(v, str):
            try:
                return Env[v]
            except KeyError:
                raise ValueError(f"Неизвестное окружение: {v}")
        return v

class StoresData(BaseModel):
    region : Region
    stors_count : int

class StocksCacheData(BaseModel):
    company_name : str
    region_id : str
    marketplace_name : str
    stcks_in_db_count : int
    stcks_in_cache_count : int
    percent : float

class CelaryData(BaseModel):
    names: list[str]
    time: list[int]
    vlaues: list[int]
