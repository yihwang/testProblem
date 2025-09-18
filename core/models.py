# 数据模型文件 - 定义请求和响应的数据结构

from pydantic import BaseModel
from typing import Optional, List
from services.spider_service import spider_service

class BriefingRequest(BaseModel):
    """舆情简报请求模型"""
    topic: str
    max_articles: int = 5  # 默认获取5篇文章

class ArticleModel(BaseModel):
    """新闻文章模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    full_text: Optional[str] = None  # 根据url获取的完整网页内容
    
    def fetch_full_text(self, request_id: str = "") -> None:
        """
        根据url字段获取完整网页内容并填充到full_text字段
        优先从数据库获取，数据库不存在时调用爬虫服务获取
        
        Args:
            request_id: 请求ID，用于日志追踪
        """
        if self.url:
            try:
                # 先从数据库检查是否已存在该文章
                from core.db_service import db_service
                existing_article = db_service.check_article_exists(self.url)
                
                if existing_article and 'full_text' in existing_article and existing_article['full_text']:
                    # 数据库中已存在完整内容，直接使用
                    self.full_text = existing_article['full_text']
                    from core.config import logger
                    logger.info(f"[{request_id}] 从数据库获取文章内容，URL: {self.url}")
                else:
                    # 数据库中不存在或没有完整内容，调用爬虫服务获取
                    self.full_text = spider_service.get_page_content(self.url, request_id)
                    
                    # 获取成功后保存到数据库
                    if self.full_text:
                        # 准备文章数据
                        article_data = {
                            'title': self.title,
                            'description': self.description,
                            'content': self.content,
                            'url': self.url,
                            'source': self.source,
                            'full_text': self.full_text
                        }
                        db_service.save_article(article_data)
            except Exception as e:
                # 在出错情况下，保持full_text为None，不抛出异常
                from core.config import logger
                logger.error(f"[{request_id}] 获取网页内容失败: {str(e)}, URL: {self.url}")

class BriefingResponse(BaseModel):
    """舆情简报响应模型"""
    request_id: str
    topic: str
    article_count: int
    summary: str
    processing_time: str

class StructuredBriefingResponse(BaseModel):
    """结构化舆情简报响应模型"""
    request_id: str
    topic: str
    article_count: int
    positive_opinion: str = ""  # 正面意见总结
    negative_concern: str = ""  # 负面关切总结
    constructive_suggestion: str = ""  # 建设性建议总结
    processing_time: str