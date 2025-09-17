# main.py
# 一个用于生成网络舆情简报的快速原型

import requests
from fastapi import FastAPI
from pydantic import BaseModel

# 1. 初始化FastAPI应用
app = FastAPI()

# 2. 定义请求体模型
class BriefingRequest(BaseModel):
    topic: str
    max_articles: int = 5 # 默认获取5篇文章

# 3. 定义API端点
@app.post("/generate_briefing")
def generate_briefing(request: BriefingRequest):
    # 打印日志，显示收到的请求
    print(f"收到请求，主题: {request.topic}")

    # --- 步骤一：从外部API获取新闻文章 ---
    NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE" 
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    
    params = {
        "q": request.topic,
        "apiKey": NEWS_API_KEY,
        "pageSize": request.max_articles,
        "language": "zh"
    }
    
    # 直接调用API，没有错误处理
    response = requests.get(NEWS_API_URL, params=params)
    articles = response.json().get("articles", [])
    
    # --- 步骤二：准备用于摘要的文本 ---
    full_text = ""
    for article in articles:
        # 简单地拼接内容，没有考虑内容为空的情况
        content = article.get("content", "")
        if content:
            full_text += content + "\n\n"

    if not full_text:
        return {"error": "未能获取到相关文章内容"}

    # --- 步骤三：调用大模型生成摘要 ---
    from transformers import pipeline

    print("正在加载摘要模型...")
    # 使用一个较小的模型作为示例，实际场景可能更大
    summarizer = pipeline("summarization", model="csebuetnlp/mT5-small")
    print("模型加载完毕。")

    # 对拼接后的长文本进行摘要
    summary = summarizer(full_text, max_length=200, min_length=50, do_sample=False)
    
    final_summary = summary[0]['summary_text']
    
    print("摘要生成完毕。")

    # --- 步骤四：返回结果 ---
    return {
        "topic": request.topic,
        "article_count": len(articles),
        "summary": final_summary
    }

# 运行应用的命令 (用于本地调试):
# uvicorn main:app --reload
