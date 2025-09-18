# 简报生成器 - 核心业务逻辑，负责协调各服务生成舆情简报

import time
from typing import List
from core.models import BriefingRequest, BriefingResponse, ArticleModel
from services.news_service import news_service
from services.summary_service import summary_service
from core.config import logger

class BriefingGenerator:
    """舆情简报生成器，负责协调各服务完成简报生成"""
    
    def __init__(self):
        # 使用导入的服务实例
        self.news_service = news_service
        self.summary_service = summary_service
    
    def generate_briefing(self, request: BriefingRequest, request_id: str) -> BriefingResponse:
        """
        生成舆情简报
        
        Args:
            request: 简报请求对象
            request_id: 请求ID，用于日志追踪
            
        Returns:
            简报响应对象
            
        Raises:
            Exception: 当处理过程中发生错误时
        """
        logger.info(f"[{request_id}] 收到请求，主题: {request.topic}, 最大文章数: {request.max_articles}")
        start_time = time.time()
        
        try:
            # 步骤一：获取新闻文章
            articles = self._get_news_articles(request.topic, request.max_articles, request_id)
            
            # 步骤二：生成摘要
            summary = self._generate_summary(articles, request_id)
            
            # 计算处理时间
            total_time = time.time() - start_time
            logger.info(f"[{request_id}] 请求处理完成，总耗时: {total_time:.2f} 秒")
            
            # 构建响应
            return BriefingResponse(
                request_id=request_id,
                topic=request.topic,
                article_count=len(articles),
                summary=summary,
                processing_time=f"{total_time:.2f}秒"
            )
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[{request_id}] 请求处理异常，总耗时: {total_time:.2f} 秒, 错误: {str(e)}")
            raise
    
    def _get_news_articles(self, topic: str, max_articles: int, request_id: str) -> List[ArticleModel]:
        """获取新闻文章的内部方法"""
        try:
            return self.news_service.get_articles(topic, max_articles, request_id)
            # return self.news_service.get_articles_from_mock("mock/mock_newsapi.json", request_id)
        except Exception as e:
            logger.error(f"[{request_id}] 获取新闻文章失败: {str(e)}")
            raise
    
    def _generate_summary(self, articles: List[ArticleModel], request_id: str) -> str:
        """生成摘要的内部方法"""
        # 转换ArticleModel对象为字典列表以便摘要服务处理
        articles_dict = [article.model_dump() for article in articles]
        
        try:
            return self.summary_service.generate_summary(articles_dict, request_id)
        except Exception as e:
            logger.error(f"[{request_id}] 生成摘要失败: {str(e)}")
            raise

# 创建单例实例供API路由使用
briefing_generator = BriefingGenerator()