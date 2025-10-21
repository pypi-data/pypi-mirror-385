import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class Log:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, console_level = logging.INFO, log_file_name="app.log"):
        self.Console_LOG_LEVEL = console_level
        self.log_file_name = log_file_name
        self.LOG_FILE_PATH = os.path.join("logs", log_file_name)
        self.logger = self.get_logger()
        self.super_log_level = self.logger.critical

    def get_logger(self):
        logger = logging.getLogger()
        # logger.setLevel(self.LOG_LEVEL)
        if not logger.handlers:
            # --- 4. 配置 Formatter (格式化器) ---
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(module)s:%(lineno)d - %(message)s"
            )
            # --- 5. 配置 Handler (处理器) ---

            # 5.1 控制台处理器 (StreamHandler)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.Console_LOG_LEVEL)  # 控制台只显示 INFO 及以上级别的日志
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)


            # 文件

            # 5.2 信息数据

            # RotatingFileHandler: 按文件大小轮转
            # maxBytes: 单个日志文件的最大字节数 (例如 10MB)
            # backupCount: 保留的旧日志文件数量
            file_handler = RotatingFileHandler(
                self.LOG_FILE_PATH,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.INFO)  # 文件中显示所有指定级别的日志
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # 5.3 错误警告日志

            file_handler_debug = RotatingFileHandler(
                self.LOG_FILE_PATH.replace('.log','_err.log'),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler_debug.setLevel(logging.WARNING)  # 文件中显示所有指定级别的日志
            file_handler_debug.setFormatter(formatter)
            logger.addHandler(file_handler_debug)
        return logger
    
    def set_super_log(self,logger_info):
        self.super_log_level = logger_info

    def super_log(self,s, target: str = "target"):
        COLOR_RED = "\033[91m"
        COLOR_GREEN = "\033[92m"
        COLOR_YELLOW = "\033[93m"
        COLOR_BLUE = "\033[94m"
        COLOR_RESET = "\033[0m" # 重置颜色
        log_ = self.super_log_level

        log_("\n"+f"{COLOR_BLUE}=={COLOR_RESET}" * 21 + target + f"{COLOR_BLUE}=={COLOR_RESET}" * 21)
        log_("\n       "+"--" * 40)
        log_(type(s))
        log_("\n       "+f"{COLOR_RED}--{COLOR_RESET}" * 40)
        log_(s)
        log_("\n"+f"{COLOR_GREEN}=={COLOR_RESET}" * 21 + target + "  end!"+f"{COLOR_GREEN}=={COLOR_RESET}" * 21)

