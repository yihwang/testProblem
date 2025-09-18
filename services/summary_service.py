# 摘要服务 - 负责使用大模型生成文本摘要

from typing import List
from transformers import pipeline
from core.config import MODEL_PATH, SUMMARY_MAX_LENGTH, SUMMARY_MIN_LENGTH, logger

class SummaryService:
    """摘要服务类，负责加载模型并生成文本摘要"""
    
    def __init__(self):
        self.model_path = MODEL_PATH
        self.summarizer = None
    
    def load_model(self, request_id: str) -> None:
        """
        加载摘要模型
        
        Args:
            request_id: 请求ID，用于日志追踪
            
        Raises:
            Exception: 当模型加载失败时
        """
        if self.summarizer is None:
            logger.info(f"[{request_id}] 正在加载摘要模型...")
            try:
                self.summarizer = pipeline(
                    "summarization", 
                    model=self.model_path, 
                    tokenizer=self.model_path, 
                    use_fast=False
                )
                logger.info(f"[{request_id}] 模型加载成功")
            except Exception as e:
                logger.error(f"[{request_id}] 模型加载失败: {str(e)}")
                raise
    
    def generate_summary(self, articles: List[dict], request_id: str) -> str:
        """
        为一组文章生成摘要
        
        Args:
            articles: 包含文章内容的字典列表
            request_id: 请求ID，用于日志追踪
            
        Returns:
            生成的摘要文本
            
        Raises:
            Exception: 当摘要生成失败时
        """
        # 加载模型（懒加载）
        self.load_model(request_id)
        
        # 准备用于摘要的文本
        full_text = ""
        for idx, article in enumerate(articles):
            try:
                content = article.get("description", "")
                if content:
                    full_text += content + "\n\n"
                    logger.debug(f"[{request_id}] 成功处理文章 {idx+1}/{len(articles)}")
            except Exception as e:
                logger.warning(f"[{request_id}] 处理文章 {idx+1} 时出错: {str(e)}")
                continue
        
        if not full_text:
            logger.warning(f"[{request_id}] 未能获取到相关文章内容")
            raise ValueError("未能获取到相关文章内容")
        
        logger.info(f"[{request_id}] 准备摘要的文本长度: {len(full_text)} 字符")
        
        # 生成摘要
        logger.info(f"[{request_id}] 开始生成摘要...")
        try:
            summary_result = self.summarizer(
                full_text, 
                max_length=SUMMARY_MAX_LENGTH, 
                min_length=SUMMARY_MIN_LENGTH, 
                do_sample=False
            )
            
            final_summary = summary_result[0]['summary_text']
            logger.info(f"[{request_id}] 摘要生成成功，摘要长度: {len(final_summary)} 字符")
            return final_summary
        except Exception as e:
            logger.error(f"[{request_id}] 摘要生成失败: {str(e)}")
            raise

# 创建单例实例供其他模块使用
summary_service = SummaryService()