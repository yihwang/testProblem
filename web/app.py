# 舆情简报服务WebUI - 使用Gradio构建的用户界面

import gradio as gr
import os
import sys
import requests
import json
from typing import Dict, Any, Optional
import time
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从项目内部导入服务和模型
from core.config import setup_logger
from core.models import BriefingRequest
from core.structured_briefing_generator import structured_briefing_generator
from core.briefing_generator import briefing_generator

# 初始化日志记录器
logger = setup_logger()

# 配置API基础URL
base_url = "http://172.18.129.32:11500"

class GradioUI:
    """舆情简报服务的Gradio用户界面"""
    
    def __init__(self):
        # 创建一个请求ID，用于日志追踪
        self.request_id = f"req_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        logger.info(f"[{self.request_id}] 初始化GradioUI")
        
    def generate_structured_briefing(self, topic: str, max_articles: int = 5, use_internal: bool = True) -> Dict[str, Any]:
        """
        生成结构化舆情简报
        
        Args:
            topic: 监控主题
            max_articles: 最大文章数量
            use_internal: 是否使用内部调用方式（不通过HTTP）
            
        Returns:
            结构化舆情简报结果字典
        """
        
        if not topic.strip():
            return {"error": "请输入有效的监控主题"}
        
        # 生成一个新的请求ID
        self.request_id = f"req_{int(time.time())}_{hash(topic) % 10000}_structured_ui"
        logger.info(f"[{self.request_id}] 收到生成结构化简报请求，主题: {topic}, 最大文章数: {max_articles}")
        
        try:
            if use_internal:
                # 使用内部调用方式
                request = BriefingRequest(topic=topic, max_articles=max_articles)
                response = structured_briefing_generator.generate_structured_briefing(request, self.request_id)
                result = response.model_dump()
            else:
                # 使用HTTP API调用方式
                url = f"{base_url}/briefing/structured"
                headers = {"Content-Type": "application/json"}
                data = json.dumps({"topic": topic, "max_articles": max_articles})
                
                logger.info(f"[{self.request_id}] 调用API: {url}")
                response = requests.post(url, headers=headers, data=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                else:
                    logger.error(f"[{self.request_id}] API调用失败，状态码: {response.status_code}, 响应: {response.text}")
                    return {"error": f"API调用失败: {response.text}"}
            
            logger.info(f"[{self.request_id}] 结构化简报生成成功")
            return result
        
        except Exception as e:
            logger.error(f"[{self.request_id}] 生成结构化简报时发生错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": f"处理失败: {str(e)}"}
    
    def create_ui(self):
        """创建Gradio用户界面"""
        with gr.Blocks(title="舆情简报服务", theme=gr.themes.Soft()) as demo:
            # 页面标题
            gr.Markdown("""# 舆情简报服务
## 输入监控主题，获取结构化舆情分析""")
            
            with gr.Row():
                # 左侧：输入区域
                with gr.Column(scale=1):
                    # 主题输入框
                    topic_input = gr.Textbox(
                        label="监控主题", 
                        placeholder="请输入要监控的主题关键词",
                        lines=2,
                        value="人工智能产业发展"
                    )
                    
                    # 最大文章数量滑块
                    max_articles_slider = gr.Slider(
                        minimum=1, 
                        maximum=20, 
                        value=5, 
                        step=1,
                        label="获取文章数量"
                    )
                    
                    # 生成按钮
                    generate_btn = gr.Button("生成结构化舆情简报", variant="primary")
                    
                    # 调用方式选择（默认使用内部调用）
                    use_internal_checkbox = gr.Checkbox(
                        value=True, 
                        label="使用内部调用（更快的响应速度）"
                    )
                    
                # 右侧：输出区域
                with gr.Column(scale=2):
                    # 响应状态
                    status_output = gr.Textbox(
                        label="处理状态", 
                        interactive=False,
                        value="就绪，请输入主题并点击生成按钮"
                    )
                    
                    # 正面意见
                    positive_output = gr.Textbox(
                        label="🔍 正面意见总结", 
                        interactive=False,
                        lines=6
                    )
                    
                    # 负面关切
                    negative_output = gr.Textbox(
                        label="⚠️ 负面关切总结", 
                        interactive=False,
                        lines=6
                    )
                    
                    # 建设性建议
                    suggestion_output = gr.Textbox(
                        label="💡 建设性建议总结", 
                        interactive=False,
                        lines=6
                    )
                    
                    # 文章数量和处理时间
                    meta_output = gr.Textbox(
                        label="元信息", 
                        interactive=False
                    )
            
            # 设置按钮点击事件
            def on_generate_click(topic, max_articles, use_internal):
                """处理生成按钮点击事件"""
                status_output = "正在生成结构化舆情简报，请稍候..."
                positive_output = ""
                negative_output = ""
                suggestion_output = ""
                meta_output = ""
                
                try:
                    # 调用生成结构化简报的方法
                    result = self.generate_structured_briefing(topic, max_articles, use_internal)
                    
                    if "error" in result:
                        # 处理错误情况
                        status_output = f"❌ 处理失败: {result['error']}"
                    else:
                        # 处理成功情况
                        status_output = "✅ 结构化舆情简报生成成功！"
                        positive_output = result.get("positive_opinion", "暂无正面意见总结")
                        negative_output = result.get("negative_concern", "暂无负面关切总结")
                        suggestion_output = result.get("constructive_suggestion", "暂无建设性建议总结")
                        meta_output = f"主题: {result.get('topic', '')}, 文章数量: {result.get('article_count', 0)}, 处理时间: {result.get('processing_time', '')}"
                except Exception as e:
                    status_output = f"❌ 处理过程中发生错误: {str(e)}"
                    logger.error(f"[{self.request_id}] 处理按钮点击事件时发生错误: {str(e)}")
                
                return status_output, positive_output, negative_output, suggestion_output, meta_output
            
            # 绑定按钮点击事件
            generate_btn.click(
                fn=on_generate_click,
                inputs=[topic_input, max_articles_slider, use_internal_checkbox],
                outputs=[status_output, positive_output, negative_output, suggestion_output, meta_output]
            )
            
            # 添加示例主题按钮
            with gr.Row():
                gr.Button("使用示例主题: 人工智能").click(
                    fn=lambda: "人工智能",
                    outputs=topic_input
                )
                gr.Button("使用示例主题: 环境保护").click(
                    fn=lambda: "环境保护",
                    outputs=topic_input
                )
                gr.Button("使用示例主题: 经济发展").click(
                    fn=lambda: "经济发展",
                    outputs=topic_input
                )
            
            # 页脚信息
            gr.Markdown("""
---
### 使用说明
1. 在监控主题输入框中输入您关心的主题关键词
2. 调整要获取的文章数量（1-20篇）
3. 点击"生成结构化舆情简报"按钮
4. 查看系统生成的正面意见、负面关切和建设性建议
5. 默认使用内部调用方式，具有更快的响应速度
""")
        
        return demo

if __name__ == "__main__":
    # 创建GradioUI实例并启动界面
    ui = GradioUI()
    demo = ui.create_ui()
    
    # 启动Gradio服务
    # 注意：如果要从其他设备访问，请设置share=True和server_name="0.0.0.0"
    demo.launch(
        server_name="0.0.0.0",
        server_port=7866,
        share=False,
        debug=True
    )