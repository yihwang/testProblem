# 测试新闻服务的fetch_full_text功能

import os
import sys
import uuid
from typing import List
from services.news_service import news_service
from core.models import ArticleModel

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_news_service_fetch_full_text():
    """
    测试NewsService是否正确调用fetch_full_text获取文章的完整网页内容
    """
    # 生成请求ID用于日志追踪
    request_id = str(uuid.uuid4())
    print(f"开始测试新闻服务的fetch_full_text功能，请求ID: {request_id}")
    
    try:
        # 使用mock文件测试，避免实际调用API
        mock_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock", "mock_newsapi.json")
        
        if not os.path.exists(mock_file_path):
            print(f"警告: mock文件不存在({mock_file_path})，将使用实际API进行测试")
            # 使用实际API测试
            articles = news_service.get_articles("人工智能", 3, request_id)
        else:
            print(f"使用mock文件进行测试: {mock_file_path}")
            articles = news_service.get_articles_from_mock(mock_file_path, request_id)
        
        # 验证结果
        if not articles:
            print("测试失败: 未获取到任何文章")
            return False
        
        print(f"成功获取到 {len(articles)} 篇文章")
        
        # 检查每篇文章是否有full_text字段，且内容不为空
        success_count = 0
        for i, article in enumerate(articles):
            if hasattr(article, 'full_text') and article.full_text:
                print(f"文章 {i+1} full_text 字段已填充，内容长度: {len(article.full_text)} 字符")
                success_count += 1
            else:
                print(f"警告: 文章 {i+1} full_text 字段为空或未填充")
        
        print(f"测试完成: 共 {success_count}/{len(articles)} 篇文章成功填充full_text字段")
        
        # 如果至少有一篇文章成功填充了full_text，则测试通过
        if success_count > 0:
            print("测试通过")
            return True
        else:
            print("测试失败: 没有文章成功填充full_text字段")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 运行测试
    result = test_news_service_fetch_full_text()
    
    # 根据测试结果设置退出码
    sys.exit(0 if result else 1)