import time
import functools
import asyncio
import os
from colorama import Fore, Style, init
from enum import Enum

# инициализация цветного вывода на Windows/Unix
init(autoreset=True)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS" 
    WARN = "WARN"
    ERORR = "ERORR"

class LoggerConfig:
    def __init__(self):
        # Уровень по умолчанию из переменной окружения или INFO
        self.level = LogLevel[os.getenv("LOG_LEVEL", "INFO")]
        self.enable_call_logging = os.getenv("ENABLE_CALL_LOGGING", "true").lower() == "true"
        
    def set_level(self, level):
        self.level = level
        
    def enable_call_logs(self, enable=True):
        self.enable_call_logging = enable

# Глобальная конфигурация
config = LoggerConfig()

# Приоритеты уровней
LOG_LEVEL_PRIORITY = {
    LogLevel.DEBUG: 10,
    LogLevel.INFO: 20,
    LogLevel.SUCCESS: 25, 
    LogLevel.WARN: 30,
    LogLevel.ERORR: 40
}

def should_log(level):
    return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[config.level]

def log_msg(message, level=LogLevel.INFO):
    if not should_log(level):
        return
        
    colors = {
        LogLevel.INFO: Fore.CYAN,
        LogLevel.DEBUG: Fore.BLUE,
        LogLevel.WARN: Fore.YELLOW,
        LogLevel.ERORR: Fore.RED,
        LogLevel.SUCCESS: Fore.GREEN
    }
    prefix = f"{colors.get(level, Fore.WHITE)}[{level.value}]{Style.RESET_ALL}"
    print(f"\n[MESSAGE]   -   {prefix} {message}\n")

def log_call(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        if not config.enable_call_logging:
            return await func(*args, **kwargs)
            
        start = time.time()
        if should_log(LogLevel.DEBUG):
            print(
                f"{Fore.CYAN}[CALL]{Style.RESET_ALL} {func.__name__}("
                f"{Fore.YELLOW}args={args}{Style.RESET_ALL}, "
                f"{Fore.YELLOW}kwargs={kwargs}{Style.RESET_ALL})"
            )
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start) * 1000
            if should_log(LogLevel.DEBUG):
                print(
                    f"{Fore.GREEN}[RETURN]{Style.RESET_ALL} {func.__name__} -> "
                    f"{Fore.MAGENTA}{result}{Style.RESET_ALL} "
                    f"({duration:.2f} ms)"
                )
            return result
        except Exception as e:
            duration = (time.time() - start) * 1000
            if should_log(LogLevel.ERORR):
                print(
                    f"{Fore.RED}[ERROR]{Style.RESET_ALL} {func.__name__} "
                    f"({duration:.2f} ms): {e}"
                )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        if not config.enable_call_logging:
            return func(*args, **kwargs)
            
        start = time.time()
        if should_log(LogLevel.DEBUG):
            print(
                f"{Fore.CYAN}[CALL]{Style.RESET_ALL} {func.__name__}("
                f"{Fore.YELLOW}args={args}{Style.RESET_ALL}, "
                f"{Fore.YELLOW}kwargs={kwargs}{Style.RESET_ALL})"
            )
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000
            if should_log(LogLevel.DEBUG):
                print(
                    f"{Fore.GREEN}[RETURN]{Style.RESET_ALL} {func.__name__} -> "
                    f"{Fore.MAGENTA}{result}{Style.RESET_ALL} "
                    f"({duration:.2f} ms)"
                )
            return result
        except Exception as e:
            duration = (time.time() - start) * 1000
            if should_log(LogLevel.ERORR):
                print(
                    f"{Fore.RED}[ERROR]{Style.RESET_ALL} {func.__name__} "
                    f"({duration:.2f} ms): {e}"
                )
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

# Утилиты для управления конфигурацией
def setup_logging(level=LogLevel.INFO, enable_calls=True):
    """Настройка логирования для приложения"""
    config.set_level(level)
    config.enable_call_logs(enable_calls)
