# 网络舆情简报生成服务

一个基于FastAPI和HuggingFace Transformers的网络舆情简报生成服务，可以根据指定主题从新闻API获取相关文章，并使用大语言模型生成摘要简报。

## 功能特点

- 根据用户指定的主题和文章数量获取相关新闻
- 自动处理和分析获取到的文章内容
- 使用预训练的大语言模型生成简洁的摘要简报
- 提供RESTful API接口便于集成
- 支持Docker容器化部署

## 安装指南

### 本地安装

1. 确保已安装Python 3.10或更高版本

2. 克隆或下载项目代码

3. 安装项目依赖
```bash
cd /data/wangyihong/testProblem
pip install -r requirements.txt
```

4. 配置News API密钥
   - 打开`testmain.py`文件
   - 将`NEWS_API_KEY`变量替换为您自己的[News API](https://newsapi.org/)密钥

5. 运行应用
```bash
uvicorn testmain:app --reload
```

### Docker部署

1. 确保已安装Docker

2. 构建Docker镜像
```bash
cd /data/wangyihong/testProblem
docker build -t舆情简报服务 .
```

3. 运行Docker容器
```bash
docker run -d -p 8000:8000 --env NEWS_API_KEY=您的API密钥 舆情简报服务
```

## API接口说明

### 生成舆情简报

**请求URL**：`/generate_briefing`

**请求方法**：POST

**请求体**：
```json
{
  "topic": "要搜索的主题",
  "max_articles": 5  # 可选，默认获取5篇文章
}
```

**响应**：
```json
{
  "topic": "请求的主题",
  "article_count": 获取到的文章数量,
  "summary": "生成的简报摘要"
}
```

## 使用示例

### 使用curl请求API

```bash
curl -X POST http://localhost:8000/generate_briefing -H "Content-Type: application/json" -d '{"topic": "人工智能", "max_articles": 3}'
```

### 使用Python请求API

```python
import requests

url = "http://localhost:8000/generate_briefing"
payload = {
    "topic": "环境保护",
    "max_articles": 5
}
response = requests.post(url, json=payload)
result = response.json()
print(f"简报摘要：{result['summary']}")
```

## 注意事项

1. 本服务依赖[News API](https://newsapi.org/)获取新闻文章，请确保您拥有有效的API密钥
2. 首次运行时，系统会自动下载预训练的摘要模型，可能需要一些时间
3. 模型下载完成后，服务响应速度将显著提高
4. 对于生产环境，建议使用更强大的摘要模型以获得更好的效果

## 开发说明

- 项目使用FastAPI框架构建Web服务
- 使用transformers库加载和使用预训练的文本摘要模型
- 代码中的摘要模型使用的是`csebuetnlp/mT5-small`，这是一个轻量级的多语言模型

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件