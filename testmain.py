# testmain.py
# 一个用于生成网络舆情简报的快速原型

import logging
import requests
import time
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("舆情简报服务")

# 1. 初始化FastAPI应用
app = FastAPI()

# 2. 定义请求体模型
class BriefingRequest(BaseModel):
    topic: str
    max_articles: int = 5 # 默认获取5篇文章

# 3. 定义API端点
@app.post("/generate_briefing")
def generate_briefing(request: BriefingRequest):
    request_id = f"req_{int(time.time())}_{hash(request.topic) % 10000}"
    logger.info(f"[{request_id}] 收到请求，主题: {request.topic}, 最大文章数: {request.max_articles}")
    start_time = time.time()

    try:
        # --- 步骤一：从外部API获取新闻文章 ---
        NEWS_API_KEY = "1c6bcc6ef29b4d819ae484c7cda9a4c5"
        NEWS_API_URL = "https://newsapi.org/v2/everything"
        
        logger.debug(f"[{request_id}] 准备调用News API，URL: {NEWS_API_URL}")
        
        params = {
            "q": request.topic,
            "apiKey": NEWS_API_KEY, 
            "pageSize": request.max_articles,
            "language": "zh"
        }
        
        try:
            # response = requests.get(NEWS_API_URL, params=params, timeout=10)
            # response.raise_for_status()  # 抛出HTTP错误
            # articles = response.json().get("articles", [])
            with open("mock/mock_newsapi.json", "r", encoding="utf-8") as f:
                articles = json.load(f).get("articles", [])
            logger.info(f"[{request_id}] 成功获取到 {len(articles)} 篇文章")
        except requests.exceptions.RequestException as e:
            logger.error(f"[{request_id}] 调用News API失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取新闻文章失败: {str(e)}")
        except Exception as e:
            logger.error(f"[{request_id}] 处理News API响应失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"处理新闻数据失败: {str(e)}")
    
        # --- 步骤二：准备用于摘要的文本 ---
        full_text = ""
        for idx, article in enumerate(articles):
            try:
                content = article.get("content", "")
                if content:
                    full_text += content + "\n\n"
                    logger.debug(f"[{request_id}] 成功处理文章 {idx+1}/{len(articles)}")
            except Exception as e:
                logger.warning(f"[{request_id}] 处理文章 {idx+1} 时出错: {str(e)}")
                continue

        if not full_text:
            logger.warning(f"[{request_id}] 未能获取到相关文章内容")
            raise HTTPException(status_code=404, detail="未能获取到相关文章内容")

        logger.info(f"[{request_id}] 准备摘要的文本长度: {len(full_text)} 字符")

        # --- 步骤三：调用大模型生成摘要 ---
        try:
            from transformers import pipeline
            
            logger.info(f"[{request_id}] 正在加载摘要模型...")
            model_start_time = time.time()
            
            # 使用一个较小的模型作为示例，实际场景可能更大
            try:
                local_model_path = "/app/mt5-small"
                summarizer = pipeline("summarization", model=local_model_path, tokenizer=local_model_path, use_fast=False)
                model_load_time = time.time() - model_start_time
                logger.info(f"[{request_id}] 模型加载完毕，耗时: {model_load_time:.2f} 秒")
            except Exception as e:
                logger.error(f"[{request_id}] 模型加载失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

            # 对拼接后的长文本进行摘要
            logger.info(f"[{request_id}] 开始生成摘要...")
            summary_start_time = time.time()
            
            try:
                summary = summarizer(full_text, max_length=200, min_length=50, do_sample=False)
                final_summary = summary[0]['summary_text']
                
                summary_time = time.time() - summary_start_time
                logger.info(f"[{request_id}] 摘要生成完毕，耗时: {summary_time:.2f} 秒，摘要长度: {len(final_summary)} 字符")
            except Exception as e:
                logger.error(f"[{request_id}] 摘要生成失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"摘要生成失败: {str(e)}")
        except ImportError as e:
            logger.error(f"[{request_id}] 导入transformers库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"导入依赖库失败: {str(e)}")

        # --- 步骤四：返回结果 ---
        total_time = time.time() - start_time
        logger.info(f"[{request_id}] 请求处理完成，总耗时: {total_time:.2f} 秒")
        
        return {
            "request_id": request_id,
            "topic": request.topic,
            "article_count": len(articles),
            "summary": final_summary,
            "processing_time": f"{total_time:.2f}秒"
        }
    except HTTPException as e:
        # 已经记录了详细日志，这里不需要重复记录
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[{request_id}] 请求处理异常，总耗时: {total_time:.2f} 秒, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时发生未知错误: {str(e)}")

# 运行应用的命令 (用于本地调试):
# uvicorn main:app --reload