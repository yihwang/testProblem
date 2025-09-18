import os
import sys 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import logging
from typing import Dict, List, Optional, Union
from openai import OpenAI, OpenAIError
from core.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_OPENAI_MODEL

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMService:
    """封装OpenAI接口的大模型服务类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, default_model: Optional[str] = None):
        """
        初始化LLM服务
        
        Args:
            api_key: OpenAI API密钥，如果未提供则从配置文件或环境变量获取
            base_url: API基础URL，用于自定义API端点，如果未提供则从配置文件获取
            default_model: 默认使用的模型名称，如果未提供则从配置文件获取
        """
        # 优先使用传入的参数，其次使用配置文件中的值
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("API密钥必须提供，可通过参数、配置文件或环境变量OPENAI_API_KEY设置")
        
        self.base_url = base_url or OPENAI_BASE_URL
        self.default_model = default_model or DEFAULT_OPENAI_MODEL
        
        # 初始化OpenAI客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        logger.info(f"LLM服务已初始化，默认模型: {self.default_model}")
    
    def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 10240,
                     temperature: float = 0.7, **kwargs) -> str:
        """
        生成文本内容
        
        Args:
            prompt: 提示文本
            model: 使用的模型名称，默认为None（使用默认模型）
            max_tokens: 最大生成token数
            temperature: 生成温度，值越高越随机
            **kwargs: 其他传递给OpenAI API的参数
        
        Returns:
            生成的文本内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # 提取生成的文本
            text = response.choices[0].message.content.strip()
            logger.info(f"文本生成成功，使用模型: {model or self.default_model}")
            return text
            
        except OpenAIError as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"文本生成过程中发生错误: {str(e)}")
            raise

llm = LLMService()

if __name__ == '__main__':
    prompt = "你是谁"
    response = llm.generate_text(prompt)
    print(response)