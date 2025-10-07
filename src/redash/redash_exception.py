from typing import Any
from loger import log_msg

class GrafanaException(Exception):
    pass

class RedashAuthException(GrafanaException):
    def __init__(self, status:int, cookies:Any, message:str="Ошибка авторизации в Redash. Корректность API ключа"):
        self.status = status
        self.cookies = cookies
        self.message = message
        super().__init__(f"STATUS: {status}\tMSG:{self.message}")

# для рефактора "когда нибудь"
class RedashRequestException(GrafanaException):
    def __init__(self, status:int, request_header:Any, requst_body:Any|None, response:Any, message:str="Ошибка при выполнении запроса к Grafana."):
        self.status = status
        self.request_header = request_header
        self.requst_body = requst_body
        self.response = response
        self.message = message

        if status > 399 and status < 500:
            self.message += " Ошибка клиента. Проверьте правильность запроса. Вероятные причины: неверный URL, неправильный метод, неверные параметры/body, вы не авторизованы."
        
        super().__init__(f"STATUS: {status}\tMSG:{self.message}\tRESPONSE:{response}\tREQUEST_HEADER:{request_header}\tREQUEST_BODY:{requst_body}")


