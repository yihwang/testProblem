# 新闻服务 - 负责调用新闻API获取相关文章

import requests
from typing import List, Optional
from core.config import NEWS_API_KEY, NEWS_API_URL, logger
from core.models import ArticleModel

class NewsService:
    """新闻服务类，负责获取和处理新闻数据"""
    
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.api_url = NEWS_API_URL
    
    def get_articles(self, topic: str, max_articles: int, request_id: str) -> List[ArticleModel]:
        """
        从新闻API获取与指定主题相关的文章
        
        Args:
            topic: 搜索主题
            max_articles: 最大文章数量
            request_id: 请求ID，用于日志追踪
            
        Returns:
            文章模型列表
        
        Raises:
            requests.exceptions.RequestException: 当API调用失败时
        """
        logger.debug(f"[{request_id}] 准备调用News API，URL: {self.api_url}")
        
        params = {
            "q": topic,
            "apiKey": self.api_key,
            "pageSize": max_articles,
            "language": "zh"
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()  # 抛出HTTP错误
            articles_data = response.json().get("articles", [])
            
            # 转换为ArticleModel对象
            articles = []
            for article_data in articles_data:
                article = ArticleModel(
                    title=article_data.get("title"),
                    description=article_data.get("description"),
                    content=article_data.get("content"),
                    url=article_data.get("url"),
                    source=article_data.get("source", {}).get("name")
                )
                articles.append(article)
            
            logger.info(f"[{request_id}] 成功获取到 {len(articles)} 篇文章")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[{request_id}] 调用News API失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[{request_id}] 处理News API响应失败: {str(e)}")
            raise
    
    def get_articles_from_mock(self, file_path: str, request_id: str) -> List[ArticleModel]:
        """
        从本地mock文件获取文章数据（用于测试）
        
        Args:
            file_path: mock文件路径
            request_id: 请求ID，用于日志追踪
            
        Returns:
            文章模型列表
        """
        import json
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles_data = data.get("articles", [])
                
                # 转换为ArticleModel对象
                articles = []
                for article_data in articles_data:
                    article = ArticleModel(
                        title=article_data.get("title"),
                        description=article_data.get("description"),
                        content=article_data.get("content"),
                        url=article_data.get("url"),
                        source=article_data.get("source", {}).get("name")
                    )
                    articles.append(article)
                
                logger.info(f"[{request_id}] 从mock文件成功获取到 {len(articles)} 篇文章")
                return articles
        except Exception as e:
            logger.error(f"[{request_id}] 读取mock文件失败: {str(e)}")
            raise

# 创建单例实例供其他模块使用
news_service = NewsService()