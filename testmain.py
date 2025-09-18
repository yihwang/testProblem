# 主入口文件 - 保持与现有代码的兼容性

# 导入新的应用入口
from api.main import app
from core.models import BriefingRequest

# 导出必要的对象供测试和其他模块使用
__all__ = ["app", "BriefingRequest"]