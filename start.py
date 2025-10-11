from app import App
from src.loger import setup_logging, log_msg, LogLevel

def start(): 
    app = App()
    app.start_app()

if __name__ == "__main__":
    setup_logging(level=LogLevel.INFO, enable_calls=True)
    try: 
        start()
    except Exception as e:
        log_msg(f"Ошибка в main: {e} \nДелаем рестарт...", LogLevel.ERORR)
        print("\n\n\n")
        start()
