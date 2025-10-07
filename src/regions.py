from enum import Enum

class Region(Enum):
    """
        Перечисление регионов с указанием названия компании, id в CMS и города (город для Redash).
        ID - это id компании из БД.
    """
    MSK = ('ООО "ФК ПУЛЬС"', 1, "Москва")
    YRS = ('ООО "ПУЛЬС Ярославль"', 2, "Ярославль")
    BRN = ('ООО "ПУЛЬС Брянск"', 4, "Брянск")
    SPB = ('ООО "ПУЛЬС СПб"', 5, "СПб")
    VLG = ('ООО "ПУЛЬС Волгоград"', 6, "Волгоград")
    VRN = ('ООО "ПУЛЬС Воронеж"', 7, "Воронеж")
    KZN = ('ООО "ПУЛЬС Казань"', 8, "Казань")
    KRN = ('ООО "ПУЛЬС Краснодар"', 9, "Краснодар")
    HBR = ('ООО "ПУЛЬС Хабаровск"', 10, "Хабаровск")
    IRK = ('ООО "ПУЛЬС Иркутск"', 11, "Иркутск")
    KRS = ('ООО "ПУЛЬС Красноярск"', 12, "Красноярск")
    EKB = ('ООО "ПУЛЬС Екатеринбург"', 13, "Екатеринбург")
    NSK = ('ООО "ПУЛЬС Новосибирск"', 14, "Новосибирск")
    SAM = ('ООО "ПУЛЬС Самара"', 15, "Самара")

    # Кортеж передается в init и присваеватся по породяку
    # Пример: company_name=ООО "ФК ПУЛЬС", cms_id=1, city=Москва
    # То есть обращаться можно так: Region.MSK.company_name, Region.MSK.id, Region.MSK.city
    def __init__(self, company_name: str, id: int, city: str):
        self._company_name = company_name
        self._id = id
        self._city = city

    @property
    def company_name(self) -> str:
        return self._company_name
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def city(self) -> str:
        return self._city