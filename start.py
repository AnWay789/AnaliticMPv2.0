from app import start, log_msg, LogLevel

try: 
    start()
except Exception as e:
    log_msg(f"Ошибка в main: {e}", LogLevel.ERORR.value)
finally:
    print("\n\n\n")
    start()
