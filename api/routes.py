# API路由 - 处理HTTP请求并调用相应的业务逻辑

import time
import fastapi
from fastapi import HTTPException
from core.models import BriefingRequest, BriefingResponse, StructuredBriefingResponse
from core.briefing_generator import briefing_generator
from core.structured_briefing_generator import structured_briefing_generator
from core.config import logger

# 创建FastAPI路由器
briefing_router = fastapi.APIRouter()

@briefing_router.post("/generate_briefing", response_model=BriefingResponse)
def generate_briefing(request: BriefingRequest):
    """
    生成舆情简报的API端点
    
    Args:
        request: 包含主题和最大文章数的请求体
        
    Returns:
        包含请求ID、主题、文章数量、摘要和处理时间的响应体
    """
    # 生成请求ID用于日志追踪
    request_id = f"req_{int(time.time())}_{hash(request.topic) % 10000}"
    
    try:
        # 调用核心业务逻辑生成简报
        response = briefing_generator.generate_briefing(request, request_id)
        return response
    except ValueError as e:
        # 处理已知的业务逻辑错误
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 处理其他未知错误
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

@briefing_router.post("/briefing/structured", response_model=StructuredBriefingResponse)
def generate_structured_briefing(request: BriefingRequest):
    """
    生成结构化舆情简报的API端点
    
    Args:
        request: 包含主题和最大文章数的请求体
        
    Returns:
        包含请求ID、主题、文章数量、正面意见、负面关切、建设性建议和处理时间的响应体
    """
    # 生成请求ID用于日志追踪
    request_id = f"req_{int(time.time())}_{hash(request.topic) % 10000}_structured"
    
    try:
        # 调用核心业务逻辑生成结构化简报
        response = structured_briefing_generator.generate_structured_briefing(request, request_id)
        return response
    except ValueError as e:
        # 处理已知的业务逻辑错误
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 处理其他未知错误
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")