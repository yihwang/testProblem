# 爬虫服务 - 负责获取网页内容

import requests
import json
from typing import Optional
from core.config import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SpiderService:
    """爬虫服务类，负责获取网页内容"""
    
    def __init__(self):
        """初始化爬虫服务"""
        # 设置请求会话，包含重试机制
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # 设置默认请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
    
    def get_page_content(self, url: str, request_id: str = "", timeout: int = 10) -> Optional[str]:
        """
        获取指定URL的网页内容
        
        Args:
            url: 要爬取的网页URL
            request_id: 请求ID，用于日志追踪
            timeout: 请求超时时间（秒）
            
        Returns:
            网页内容字符串，如果失败则返回None
        """
        try:
            logger.info(f"[{request_id}] 开始爬取网页: {url}")
            
            # 发送请求获取网页内容
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()  # 抛出HTTP错误
            
            # 根据响应头设置编码
            if 'charset' in response.headers.get('content-type', '').lower():
                response.encoding = response.apparent_encoding
            
            content = response.text
            logger.info(f"{content[:500]}")
            logger.info(f"[{request_id}] 成功获取网页内容，大小: {len(content)} 字符")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[{request_id}] 爬取网页失败: {str(e)}, URL: {url}")
            return None
        except Exception as e:
            logger.error(f"[{request_id}] 处理网页内容时发生错误: {str(e)}, URL: {url}")
            return None
    
    def get_json_content(self, url: str, request_id: str = "", timeout: int = 10) -> Optional[dict]:
        """
        获取指定URL的JSON内容
        
        Args:
            url: 要爬取的网页URL
            request_id: 请求ID，用于日志追踪
            timeout: 请求超时时间（秒）
            
        Returns:
            JSON解析后的字典，如果失败则返回None
        """
        try:
            logger.info(f"[{request_id}] 开始获取JSON内容: {url}")
            
            # 发送请求获取JSON内容
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()  # 抛出HTTP错误
            
            json_data = response.json()
            logger.info(f"[{request_id}] 成功获取JSON内容")
            
            return json_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] 解析JSON失败: {str(e)}, URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"[{request_id}] 获取JSON内容失败: {str(e)}, URL: {url}")
            return None
        except Exception as e:
            logger.error(f"[{request_id}] 处理JSON内容时发生错误: {str(e)}, URL: {url}")
            return None

# 创建单例实例供其他模块使用
spider_service = SpiderService()