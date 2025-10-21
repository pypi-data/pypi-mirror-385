from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(".env", override=True)

from .log import Log
import logging
Log_ = Log(console_level = logging.WARNING, 
             log_file_name="app.log")
logger = Log_.logger
Log_.set_super_log(logger.critical)

super_log = Log_.super_log # 调试工具
inference_save_case = False