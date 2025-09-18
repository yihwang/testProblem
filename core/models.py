# 数据模型文件 - 定义请求和响应的数据结构

from pydantic import BaseModel
from typing import Optional, List

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