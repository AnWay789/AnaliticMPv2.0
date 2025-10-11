from app import App
from src.loger import log_call, log_msg, LogLevel

try: 
    app = App()
    app.start_app()
except Exception as e:
    log_msg(f"Ошибка в main: {e}", LogLevel.ERORR.value)
finally:
    print("\n\n\n")
    app.start_app()
