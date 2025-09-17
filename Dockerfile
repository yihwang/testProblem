# 使用国内镜像源加速
FROM docker.m.daocloud.io/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 使用国内pip源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 复制requirements.txt文件到工作目录
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY testmain.py .

# 设置环境变量
ENV NEWS_API_KEY=YOUR_NEWS_API_KEY_HERE

# 暴露应用端口
EXPOSE 11500

# 启动应用
CMD ["uvicorn", "testmain:app", "--host", "0.0.0.0", "--port", "11500"]