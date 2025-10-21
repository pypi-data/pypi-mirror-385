
from pro_craft.prompt_helper import IntellectType,Intel

intels = Intel(model_name="doubao-1-5-pro-256k-250115")


result = intels.sync_prompt_data_to_database("mysql+pymysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2-test")