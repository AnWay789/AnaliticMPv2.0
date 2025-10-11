from app import App
from src.loger import setup_logging, log_msg, LogLevel

try: 
    app = App()
    setup_logging(level=LogLevel.INFO, enable_calls=True)
    app.start_app()
except Exception as e:
    log_msg(f"Ошибка в main: {e}", LogLevel.ERORR)
finally:
    print("\n\n\n")
    app.start_app()
