# 应用主入口 - 初始化FastAPI应用并注册路由

from fastapi import FastAPI
from api.routes import briefing_router
from core.config import setup_logger

# 初始化FastAPI应用
app = FastAPI(
    title="舆情简报服务",
    description="一个用于生成网络舆情简报的快速原型",
    version="1.0.0"
)

# 注册API路由
app.include_router(briefing_router)

# 初始化日志记录器
logger = setup_logger()

# 健康检查端点
@app.get("/")
def health_check():
    """服务健康检查端点"""
    return {"status": "ok", "message": "舆情简报服务正在运行"}