import json
import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入被测试的模块
from testmain import app, BriefingRequest

# 创建测试客户端
client = TestClient(app)

# 模拟新闻API响应
mock_news_response = {
    "articles": [
        {
            "description": "这是第一条新闻的描述，内容关于人工智能的最新发展。人工智能技术正在快速进步，应用领域越来越广泛。",
            "content": "这是第一条新闻的完整内容，详细介绍了人工智能的最新发展和应用场景。"
        },
        {
            "description": "这是第二条新闻的描述，内容关于环保政策的新变化。政府出台了一系列新政策来促进环境保护和可持续发展。",
            "content": "这是第二条新闻的完整内容，详细介绍了新环保政策的具体措施和预期影响。"
        }
    ]
}

# 模拟摘要结果
mock_summary_result = [
    {"summary_text": "这是一段模拟的摘要结果，包含了新闻的主要信息和关键点。"}
]


class TestBriefingGeneration:
    
    @patch('testmain.requests.get')
    @patch('testmain.pipeline')
    def test_successful_briefing_generation(self, mock_pipeline, mock_get):
        """测试正常情况下的舆情简报生成功能"""
        # 配置mock对象
        mock_response = MagicMock()
        mock_response.json.return_value = mock_news_response
        mock_get.return_value = mock_response
        
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = mock_summary_result
        mock_pipeline.return_value = mock_summarizer
        
        # 发送测试请求
        response = client.post(
            "/generate_briefing",
            json={"topic": "人工智能", "max_articles": 2}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "人工智能"
        assert data["article_count"] == 2
        assert "summary" in data
        assert data["summary"] == "这是一段模拟的摘要结果，包含了新闻的主要信息和关键点。"
        assert "request_id" in data
        assert "processing_time" in data
        
        # 验证mock对象被正确调用
        mock_get.assert_called_once()
        mock_pipeline.assert_called_once()
    
    @patch('testmain.requests.get')
    def test_no_articles_found(self, mock_get):
        """测试未找到相关文章的情况"""
        # 配置mock对象返回空的文章列表
        mock_response = MagicMock()
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response
        
        # 发送测试请求
        response = client.post(
            "/generate_briefing",
            json={"topic": "不存在的主题", "max_articles": 5}
        )
        
        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "未能获取到相关文章内容"
    
    @patch('testmain.requests.get')
    def test_news_api_error(self, mock_get):
        """测试新闻API调用失败的情况"""
        # 配置mock对象抛出异常
        mock_get.side_effect = Exception("API调用失败")
        
        # 发送测试请求
        response = client.post(
            "/generate_briefing",
            json={"topic": "科技", "max_articles": 5}
        )
        
        # 验证响应
        assert response.status_code == 500
        data = response.json()
        assert "获取新闻文章失败" in data["detail"]
    
    @patch('testmain.requests.get')
    @patch('testmain.pipeline')
    def test_summary_generation_error(self, mock_pipeline, mock_get):
        """测试摘要生成失败的情况"""
        # 配置mock对象
        mock_response = MagicMock()
        mock_response.json.return_value = mock_news_response
        mock_get.return_value = mock_response
        
        # 配置pipeline抛出异常
        mock_pipeline.side_effect = Exception("模型加载失败")
        
        # 发送测试请求
        response = client.post(
            "/generate_briefing",
            json={"topic": "科技", "max_articles": 2}
        )
        
        # 验证响应
        assert response.status_code == 500
        data = response.json()
        assert "模型加载失败" in data["detail"]
    
    @patch('builtins.open', new_callable=MagicMock)
    @patch('testmain.pipeline')
    def test_mock_data_loading(self, mock_pipeline, mock_open):
        """测试使用本地mock数据的情况"""
        # 配置mock对象
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(mock_news_response)
        mock_open.return_value = mock_file
        
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = mock_summary_result
        mock_pipeline.return_value = mock_summarizer
        
        # 发送测试请求
        with patch('testmain.requests.get', side_effect=Exception("强制使用mock数据")):
            response = client.post(
                "/generate_briefing",
                json={"topic": "测试", "max_articles": 2}
            )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["article_count"] == 2
    
    def test_invalid_input_validation(self):
        """测试输入验证功能"""
        # 测试缺少必填字段
        response = client.post(
            "/generate_briefing",
            json={"max_articles": 5}  # 缺少topic字段
        )
        assert response.status_code == 422  # 验证错误
        
        # 测试无效的max_articles值
        response = client.post(
            "/generate_briefing",
            json={"topic": "科技", "max_articles": 0}  # max_articles不能为0
        )
        assert response.status_code == 422  # 验证错误
    
    @patch('testmain.requests.get')
    @patch('testmain.pipeline')
    def test_edge_case_max_articles(self, mock_pipeline, mock_get):
        """测试max_articles的边界情况"""
        # 配置mock对象
        mock_response = MagicMock()
        mock_response.json.return_value = mock_news_response
        mock_get.return_value = mock_response
        
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = mock_summary_result
        mock_pipeline.return_value = mock_summarizer
        
        # 测试最大值
        response = client.post(
            "/generate_briefing",
            json={"topic": "科技", "max_articles": 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["max_articles"] == 100  # 应该保持请求中的值
    
    @patch('testmain.requests.get')
    @patch('testmain.pipeline')
    def test_empty_article_content(self, mock_pipeline, mock_get):
        """测试文章内容为空的情况"""
        # 配置mock对象返回内容为空的文章
        empty_content_response = {
            "articles": [
                {"description": "", "content": ""},
                {"description": "", "content": ""}
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = empty_content_response
        mock_get.return_value = mock_response
        
        # 发送测试请求
        response = client.post(
            "/generate_briefing",
            json={"topic": "测试", "max_articles": 2}
        )
        
        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "未能获取到相关文章内容"


if __name__ == "__main__":
    pytest.main(["-v", __file__])