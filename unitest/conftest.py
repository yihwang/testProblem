import os
import sys
import pytest
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 保存原始的环境变量
    original_env = dict(os.environ)
    
    # 设置测试环境变量
    os.environ["NEWS_API_KEY"] = "test_api_key"
    
    # 在测试运行前执行
    yield
    
    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_news_api():
    """提供模拟的新闻API响应"""
    with patch('testmain.requests.get') as mock_get:
        # 配置基本的模拟响应
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "articles": [
                {
                    "description": "测试新闻描述1",
                    "content": "测试新闻内容1"
                },
                {
                    "description": "测试新闻描述2",
                    "content": "测试新闻内容2"
                }
            ]
        }
        
        yield mock_get


@pytest.fixture
def mock_summary_pipeline():
    """提供模拟的摘要生成pipeline"""
    with patch('testmain.pipeline') as mock_pipeline:
        # 配置模拟的摘要结果
        mock_summarizer = mock_pipeline.return_value
        mock_summarizer.return_value = [{"summary_text": "这是一段模拟的摘要结果"}]
        
        yield mock_pipeline


@pytest.fixture
def mock_file_read():
    """提供模拟的文件读取功能"""
    with patch('builtins.open') as mock_open:
        yield mock_open


@pytest.fixture
def test_client():
    """提供FastAPI测试客户端"""
    from fastapi.testclient import TestClient
    from testmain import app
    
    return TestClient(app)


def pytest_addoption(parser):
    """添加pytest命令行选项"""
    parser.addoption(
        "--run-slow", action="store_true", default=False,
        help="运行慢速测试（如实际API调用）"
    )


def pytest_configure(config):
    """配置pytest"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: mark test as slow to run"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """根据命令行选项调整测试收集"""
    if not config.getoption("--run-slow"):
        # 跳过标记为slow的测试
        skip_slow = pytest.mark.skip(reason="需要--run-slow选项来运行")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)