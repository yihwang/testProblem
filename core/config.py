# 配置文件 - 存储应用的全局配置信息

import logging
import os
from typing import Optional

# 配置日志
def setup_logger() -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger("舆情简报服务")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 文件处理器
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    
    return logger

# 获取日志记录器
logger = setup_logger()

# API配置
NEWS_API_KEY: str = "xxx"
NEWS_API_URL: str = "https://newsapi.org/v2/everything"

# 模型配置
MODEL_PATH: str = os.path.dirname(os.path.dirname(__file__)) + "/mt5-small"

# 摘要配置
SUMMARY_MAX_LENGTH: int = 200
SUMMARY_MIN_LENGTH: int = 50

# 默认值
DEFAULT_MAX_ARTICLES: int = 5

# 是否需要根据URL获取新闻全文
FETCH_FULL_TEXT: bool = False

# OpenAI接口模型配置
OPENAI_API_KEY: Optional[str] = "xxx"
OPENAI_BASE_URL: Optional[str] = "https://api.vveai.com/v1"
DEFAULT_OPENAI_MODEL: str = "qwen3-32b"