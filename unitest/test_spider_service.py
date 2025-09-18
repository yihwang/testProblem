# 爬虫服务测试脚本

import uuid
from services.spider_service import spider_service
from core.config import logger

def test_spider_service():
    """测试爬虫服务功能"""
    logger.info("开始测试爬虫服务功能")
    
    # 生成唯一的测试ID
    test_id = str(uuid.uuid4())[:8]
    request_id = f"test_spider_{test_id}"
    
    # 测试URL列表（包含不同类型的网站）
    test_urls = [
        "https://www.example.com",  # 简单测试用网站
        "https://36kr.com/p/3468634296866432"  # 用户提到的URL
    ]
    
    results = []
    
    for url in test_urls:
        try:
            logger.info(f"[{request_id}] 测试URL: {url}")
            
            # 调用爬虫服务获取网页内容
            content = spider_service.get_page_content(url, request_id)
            
            if content:
                # 验证内容
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.info(f"[{request_id}] 成功获取网页内容，长度: {len(content)} 字符")
                logger.debug(f"[{request_id}] 内容预览: {content_preview}")
                
                results.append({
                    "url": url,
                    "success": True,
                    "content_length": len(content)
                })
            else:
                logger.error(f"[{request_id}] 获取网页内容失败")
                
                results.append({
                    "url": url,
                    "success": False,
                    "error": "Content is None"
                })
                
        except Exception as e:
            logger.error(f"[{request_id}] 测试过程中发生错误: {str(e)}")
            
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
        
        # 测试之间添加短暂延迟，避免请求过于频繁
        import time
        time.sleep(1)
    
    # 输出测试总结
    logger.info("爬虫服务测试总结:")
    success_count = sum(1 for result in results if result["success"])
    
    for i, result in enumerate(results):
        if result["success"]:
            logger.info(f"  测试 {i+1}: URL={result['url']}，成功，内容长度={result['content_length']} 字符")
        else:
            logger.info(f"  测试 {i+1}: URL={result['url']}，失败，错误={result['error']}")
    
    logger.info(f"测试完成，成功{success_count}/{len(results)}个URL")
    
    return {
        "success": success_count > 0,
        "total_tests": len(results),
        "success_count": success_count,
        "results": results
    }

if __name__ == "__main__":
    result = test_spider_service()
    if result["success"]:
        logger.info("爬虫服务测试通过！")
    else:
        logger.error("爬虫服务测试失败！")