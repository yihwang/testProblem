# 测试数据库服务功能

import uuid
from core.db_service import db_service
from core.models import ArticleModel


def test_database_persistence():
    """测试数据库持久化功能"""
    print("开始测试数据库持久化功能...")
    
    # 创建一个测试用的请求ID
    request_id = str(uuid.uuid4())
    
    # 测试用例1: 检查不存在的文章
    test_url = "https://www.example.com/test1"
    print(f"\n测试用例1: 检查不存在的文章，URL: {test_url}")
    
    existing_article = db_service.check_article_exists(test_url)
    if existing_article is None:
        print("✓ 正确返回None，表示文章不存在")
    else:
        print("✗ 测试失败: 应该返回None但返回了数据")
    
    # 测试用例2: 保存文章到数据库
    print("\n测试用例2: 保存文章到数据库")
    
    article_data = {
        'title': '测试文章标题',
        'description': '这是一篇测试文章的描述',
        'content': '这是测试文章的主要内容',
        'url': test_url,
        'source': '测试来源',
        'full_text': '这是通过爬虫获取的完整网页内容'
    }
    
    save_result = db_service.save_article(article_data)
    if save_result:
        print("✓ 成功保存文章到数据库")
    else:
        print("✗ 保存文章失败")
    
    # 测试用例3: 检查已存在的文章
    print("\n测试用例3: 检查已存在的文章")
    
    existing_article = db_service.check_article_exists(test_url)
    if existing_article:
        print(f"✓ 成功找到文章，标题: {existing_article.get('title')}")
        print(f"   URL: {existing_article.get('url')}")
        print(f"   完整内容长度: {len(existing_article.get('full_text', ''))} 字符")
    else:
        print("✗ 未能找到已保存的文章")
    
    # 测试用例4: 使用ArticleModel的fetch_full_text方法
    print("\n测试用例4: 使用ArticleModel的fetch_full_text方法")
    
    article = ArticleModel(
        title="新的测试文章标题",
        url=test_url,
        source="测试来源"
    )
    
    # 调用fetch_full_text方法，应该从数据库获取内容
    article.fetch_full_text(request_id)
    
    if article.full_text:
        print("✓ 成功从数据库获取文章内容")
        print(f"   内容长度: {len(article.full_text)} 字符")
    else:
        print("✗ 未能获取文章内容")
    
    # 测试用例5: 使用新的URL调用fetch_full_text方法
    print("\n测试用例5: 使用新的URL调用fetch_full_text方法")
    
    new_test_url = "https://www.example.com/test2"
    new_article = ArticleModel(
        title="另一个测试文章",
        url=new_test_url,
        source="测试来源"
    )
    
    # 由于这是一个新的URL，应该调用爬虫服务获取内容
    # 注意：由于我们使用的是示例URL，爬虫服务可能无法获取实际内容
    # 但我们可以验证调用过程是否正确
    try:
        new_article.fetch_full_text(request_id)
        print("✓ 成功调用fetch_full_text方法")
        
        # 检查是否尝试保存到数据库（即使内容为空）
        # 由于我们使用的是示例URL，实际可能无法获取内容
        # 所以这里只检查调用过程是否正常
        
        # 再次创建一个文章，这次使用已有的URL来验证数据库优先逻辑
        verify_article = ArticleModel(url=test_url)
        verify_article.fetch_full_text(request_id)
        if verify_article.full_text:
            print("✓ 验证：成功从数据库获取已有文章的内容")
        else:
            print("✗ 验证失败：未能从数据库获取已有文章的内容")
    except Exception as e:
        print(f"✗ 调用fetch_full_text方法时出错: {str(e)}")
    
    print("\n测试完成！")


if __name__ == "__main__":
    test_database_persistence()