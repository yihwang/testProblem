# 结构化舆情简报生成器 - 负责从舆情内容中提取三个核心维度

import time
import json
from typing import List, Tuple
from core.models import BriefingRequest, StructuredBriefingResponse, ArticleModel
from services.news_service import news_service
from services.llm_service import llm
from core.config import logger

class StructuredBriefingGenerator:
    """结构化舆情简报生成器，负责从舆情内容中提取三个核心维度"""
    
    def __init__(self):
        # 使用导入的服务实例
        self.news_service = news_service
    
    def generate_structured_briefing(self, request: BriefingRequest, request_id: str) -> StructuredBriefingResponse:
        """
        生成结构化舆情简报
        
        Args:
            request: 简报请求对象
            request_id: 请求ID，用于日志追踪
            
        Returns:
            结构化简报响应对象
            
        Raises:
            Exception: 当处理过程中发生错误时
        """
        logger.info(f"[{request_id}] 收到结构化简报请求，主题: {request.topic}, 最大文章数: {request.max_articles}")
        start_time = time.time()
        
        try:
            # 步骤一：获取新闻文章
            articles = self._get_news_articles(request.topic, request.max_articles, request_id)
            
            # 步骤二：结构化提取三个核心维度
            positive_opinions, negative_concerns, constructive_suggestions = \
                self._extract_structured_content(articles, request.topic, request_id)
            
            # 步骤三：对结构化内容进行总结
            positive_opinion, negative_concern, constructive_suggestion = \
                self._summarize_structured_content(positive_opinions, negative_concerns, constructive_suggestions, request.topic, request_id)
            
            # 计算处理时间
            total_time = time.time() - start_time
            logger.info(f"[{request_id}] 结构化简报处理完成，总耗时: {total_time:.2f} 秒")
            
            # 构建响应
            return StructuredBriefingResponse(
                request_id=request_id,
                topic=request.topic,
                article_count=len(articles),
                positive_opinion=positive_opinion,
                negative_concern=negative_concern,
                constructive_suggestion=constructive_suggestion,
                processing_time=f"{total_time:.2f}秒"
            )
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[{request_id}] 结构化简报处理异常，总耗时: {total_time:.2f} 秒, 错误: {str(e)}")
            raise
    
    def _get_news_articles(self, topic: str, max_articles: int, request_id: str) -> List[ArticleModel]:
        """获取新闻文章的内部方法"""
        try:
            # return self.news_service.get_articles(topic, max_articles, request_id)
            return self.news_service.get_articles_from_mock("mock/mock_newsapi.json", request_id)
        except Exception as e:
            logger.error(f"[{request_id}] 获取新闻文章失败: {str(e)}")
            raise

    def _extract_structured_content_by_llm(self, articles: List[ArticleModel], topic: str, request_id: str):
        """
        通过大语言模型从文章中结构化提取三个核心维度
        
        Args:
            articles: 文章模型列表
            topic: 简报主题
            request_id: 请求ID，用于日志追踪
        
        Returns:
            包含正面意见、负面关切和建设性建议的元组
        """
        # 初始化结果列表
        positive_opinions = []
        negative_concerns = []
        constructive_suggestions = []
        
        # 处理每篇文章
        for idx, article in enumerate(articles):
            try:
                # 获取文章标题和内容
                title = article.title
                description = article.description
                
                if not title and not description:
                    logger.warning(f"[{request_id}] 跳过空文章 {idx+1}/{len(articles)}")
                    continue
                
                # 构建提示词
                prompt = """### 角色：你是一个专业的舆情分析师，负责从新闻文章中提取正面意见、负面关切和建设性建议。
### 任务：请分析以下新闻文章，围绕#{topic}#主题，提取出其中的正面意见、负面关切和建设性建议。
### 思考流程：
1. 首先判断新闻主旨是属于提出正面意见、还是负面关切或者是提出建设性建议
2. 如果是正面意见，将其添加到正面意见列表中
3. 如果是负面关切，将其添加到负面关切列表中
4. 如果是建设性建议，将其添加到建设性建议列表中
5. 文章中可能同时包含以上三种维度的内容
6. 和主题不相关的意见直接忽略，不要提取
### 输出格式：
{{"positive_opinions": [], "negative_concerns": [], "constructive_suggestions": []}}
不要输出其他内容
### 文章内容：
# 标题：{title}
# 摘要：{description}
"""
                
                # 调用LLM服务
                logger.info(f"[{request_id}] 调用LLM服务处理文章 {idx+1}/{len(articles)}")
                response = llm.generate_text(prompt.format(topic=topic, title=title, description=description))
                
                # 解析JSON响应
                try:
                    # 清理响应内容，移除可能包含的```json ```标记
                    response = response.lstrip("```json").rstrip("```")
                    result = json.loads(response)
                    logger.info(result)
                    
                    # 合并结果
                    if "positive_opinions" in result and isinstance(result["positive_opinions"], list):
                        positive_opinions.extend(result["positive_opinions"])
                    
                    if "negative_concerns" in result and isinstance(result["negative_concerns"], list):
                        negative_concerns.extend(result["negative_concerns"])
                    
                    if "constructive_suggestions" in result and isinstance(result["constructive_suggestions"], list):
                        constructive_suggestions.extend(result["constructive_suggestions"])
                    
                    logger.info(f"[{request_id}] 成功解析文章 {idx+1} 的结构化内容")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[{request_id}] 解析文章 {idx+1} 的响应JSON失败: {str(e)}, 响应内容: {response}")
                    continue
                
            except Exception as e:
                import traceback
                logger.error(traceback.format_exc())
                logger.error(f"[{request_id}] 处理文章 {idx+1} 时发生错误: {str(e)}")
                continue
        
        # 去重处理
        positive_opinions = list(set(positive_opinions))
        negative_concerns = list(set(negative_concerns))
        constructive_suggestions = list(set(constructive_suggestions))
        
        logger.info(f"[{request_id}] LLM结构化提取完成，正面意见: {len(positive_opinions)}, 负面关切: {len(negative_concerns)}, 建设性建议: {len(constructive_suggestions)}")
        
        return positive_opinions, negative_concerns, constructive_suggestions
    
    def _extract_structured_content(self, articles: List[ArticleModel], topic: str, request_id: str) -> Tuple[List[str], List[str], List[str]]:
        """
        从文章中结构化提取三个核心维度
        
        Args:
            articles: 文章模型列表
            topic: 简报主题
            request_id: 请求ID，用于日志追踪
            
        Returns:
            包含正面意见、负面关切和建设性建议的元组
        """
        if not articles:
            logger.warning(f"[{request_id}] 文章列表为空")
            return [], [], []
        
        logger.info(f"[{request_id}] 开始从 {len(articles)} 篇文章中结构化提取内容")
        
        # 调用LLM服务进行结构化内容提取
        try:
            positive_opinions, negative_concerns, constructive_suggestions = self._extract_structured_content_by_llm(articles, topic, request_id)
            
            logger.info(f"[{request_id}] 结构化提取完成，正面意见: {len(positive_opinions)}, 负面关切: {len(negative_concerns)}, 建设性建议: {len(constructive_suggestions)}")
            
            return positive_opinions, negative_concerns, constructive_suggestions
            
        except Exception as e:
            logger.error(f"[{request_id}] 结构化内容提取过程中发生错误: {str(e)}")
            # 提取失败时返回空列表
            return [], [], []
        
    def _summarize_structured_content(self, positive_opinions: List[str], negative_concerns: List[str], constructive_suggestions: List[str], topic: str, request_id: str) -> Tuple[str, str, str]:
        """
        对结构化提取的内容进行总结
        
        Args:
            positive_opinions: 正面意见列表
            negative_concerns: 负面关切列表
            constructive_suggestions: 建设性建议列表
            topic: 简报主题
            request_id: 请求ID，用于日志追踪
            
        Returns:
            包含正面意见总结、负面关切总结和建设性建议总结的元组
        """
        logger.info(f"[{request_id}] 开始对结构化内容进行总结")
        
        # 初始化总结结果
        positive_opinion_summary = ""
        negative_concern_summary = ""
        constructive_suggestion_summary = ""

        prompt = """### 角色：你是一个专业的舆情分析师。
### 任务：请围绕#{topic}#主题，对以内容进行总结，生成一段简洁明了的总结文字。
### 思考流程：
1. 对正面意见、负面关切和建设性建议分别进行总结
2. 如果列表为空，直接返回空字符串
### 要求：
1. 总结要涵盖主要观点
2. 语言简洁，避免重复
3. 保持原有的情感色彩
4. 直接输出总结结果，不要添加其他说明
### 输出格式：
{{"positive_opinions": "xxx", "negative_concerns": "xxx", "constructive_suggestions": "xxx"}}
### 需要总结的内容：
# 正面意见：{positive_opinions}
# 负面关切：{negative_concerns}
# 建设性建议：{constructive_suggestions}
"""

        try:
            # 格式化提示词
            formatted_prompt = prompt.format(
                topic=topic,
                positive_opinions="\n".join([f"- {item}" for item in positive_opinions]) if positive_opinions else "无",
                negative_concerns="\n".join([f"- {item}" for item in negative_concerns]) if negative_concerns else "无",
                constructive_suggestions="\n".join([f"- {item}" for item in constructive_suggestions]) if constructive_suggestions else "无"
            )
            
            # 调用LLM服务
            logger.info(f"[{request_id}] 调用LLM服务进行结构化内容总结")
            response = llm.generate_text(formatted_prompt)
            
            # 清理响应结果
            response_clean = response.strip()
            logger.info(f"[{request_id}] LLM服务返回总结结果: {response_clean}")
            
            # 解析JSON格式结果
            summary_data = json.loads(response_clean)
            
            # 提取各个总结结果
            positive_opinion_summary = summary_data.get("positive_opinions", "")
            negative_concern_summary = summary_data.get("negative_concerns", "")
            constructive_suggestion_summary = summary_data.get("constructive_suggestions", "")
            
            logger.info(f"[{request_id}] 结构化内容总结完成")
            
        except Exception as e:
            logger.error(f"[{request_id}] 结构化内容总结过程中发生错误: {str(e)}")
            # 总结失败时返回空字符串
            return "", "", ""
                
        return positive_opinion_summary, negative_concern_summary, constructive_suggestion_summary


# 创建单例实例供API路由使用
structured_briefing_generator = StructuredBriefingGenerator()