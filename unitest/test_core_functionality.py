import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# 导入被测试的模块
from testmain import app, BriefingRequest

# 创建测试客户端
client = TestClient(app)


class TestCoreFunctionality:
    
    def test_basic_endpoint_availability(self):
        """测试API端点基本可用性"""
        # 使用OPTIONS请求检查端点是否存在
        response = client.options("/generate_briefing")
        assert response.status_code == 200
        # 检查是否支持POST方法
        assert "POST" in response.headers.get("allow", "")
    
    def test_request_model_validation(self):
        """测试请求模型验证"""
        # 测试有效的请求格式
        valid_request = {"topic": "测试主题", "max_articles": 3}
        # 由于我们只是验证请求格式，使用mock来避免实际执行
        with patch('testmain.generate_briefing') as mock_generate:
            mock_generate.return_value = {
                "request_id": "test_id",
                "topic": "测试主题",
                "article_count": 0,
                "summary": "",
                "processing_time": "0.00秒"
            }
            response = client.post("/generate_briefing", json=valid_request)
            assert response.status_code == 200
    
    @patch('testmain.open')
    @patch('testmain.pipeline')
    def test_mock_data_integration(self, mock_pipeline, mock_open):
        """测试使用本地mock数据的集成功能"""
        # 配置mock文件读取
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({
            "articles": [
                {"description": "测试新闻1", "content": "这是第一条测试新闻的详细内容。"},
                {"description": "测试新闻2", "content": "这是第二条测试新闻的详细内容。"}
            ]
        })
        mock_open.return_value = mock_file
        
        # 配置mock摘要生成
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = [{"summary_text": "这是测试新闻的摘要结果。"}]
        mock_pipeline.return_value = mock_summarizer
        
        # 发送请求
        with patch('testmain.requests.get', side_effect=Exception("强制使用mock数据")):
            response = client.post(
                "/generate_briefing",
                json={"topic": "测试", "max_articles": 2}
            )
        
        # 验证响应包含所有必要字段
        assert response.status_code == 200
        data = response.json()
        assert all(key in data for key in ["request_id", "topic", "article_count", "summary", "processing_time"])
        assert data["article_count"] == 2
        assert data["summary"] == "这是测试新闻的摘要结果。"


@pytest.mark.slow  # 标记为慢速测试
@patch('testmain.pipeline')
def test_error_handling_chain(mock_pipeline):
    """测试完整的错误处理链"""
    # 配置不同的错误场景
    error_scenarios = [
        # (模拟的异常, 预期的状态码, 预期的错误信息片段)
        (Exception("API调用超时"), 500, "获取新闻文章失败"),
        (ValueError("无效的响应格式"), 500, "处理新闻数据失败"),
        (Exception("模型加载错误"), 500, "模型加载失败")
    ]
    
    for exception, status_code, error_message in error_scenarios:
        with patch('testmain.requests.get', side_effect=exception):
            response = client.post(
                "/generate_briefing",
                json={"topic": "测试", "max_articles": 5}
            )
            
            assert response.status_code == status_code
            assert error_message in response.json()["detail"]


# 可以添加更多针对特定功能的测试用例
# 例如：测试日志记录、测试性能指标、测试并发请求等

if __name__ == "__main__":
    pytest.main(["-v", __file__])