from app import App
from src.loger import setup_logging, log_msg, LogLevel

def start(): 
    setup_logging(level=LogLevel.INFO, enable_calls=True)
    try: 
        app = App()
        app.start_app()
    except Exception as e:
        log_msg(f"Ошибка в main: {e} \nДелаем рестарт...", LogLevel.ERORR)
        print("\n\n\n")
        start()

if __name__ == "__main__":
    start()
