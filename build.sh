#!/bin/bash

# 设置默认镜像名称和标签
IMAGE_NAME="public-opinion-service"
IMAGE_TAG="v1"

# 检查Docker是否已安装
if ! command -v docker &> /dev/null
then
    echo "错误: Docker未安装，请先安装Docker。"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker守护进程是否运行
if ! docker info &> /dev/null
then
    echo "错误: Docker守护进程未运行，请先启动Docker。"
    exit 1
fi

# 可选：允许用户自定义镜像名称和标签
read -p "请输入镜像名称 [默认: $IMAGE_NAME]: " user_image_name
read -p "请输入镜像标签 [默认: $IMAGE_TAG]: " user_image_tag

# 如果用户输入了值，则使用用户输入的值
if [ -n "$user_image_name" ]
then
    IMAGE_NAME=$user_image_name
fi

if [ -n "$user_image_tag" ]
then
    IMAGE_TAG=$user_image_tag
fi

# 构建完整的镜像标识符
IMAGE_ID="$IMAGE_NAME:$IMAGE_TAG"

# 打印构建信息
echo "正在构建Docker镜像: $IMAGE_ID"

# 执行构建命令
# 注意：这里使用的是当前目录的Dockerfile，端口已改为11500
docker build -t "$IMAGE_ID" .

# 检查构建是否成功
if [ $? -eq 0 ]
then
    echo "\n✅ Docker镜像构建成功！"
    echo "\n镜像信息："
    echo "- 镜像名称: $IMAGE_NAME"
    echo "- 镜像标签: $IMAGE_TAG"
    echo "- 完整标识符: $IMAGE_ID"
    
    echo "\n📋 使用指南："
    echo "1. 运行镜像（替换YOUR_NEWS_API_KEY为您的News API密钥）："
    echo "   docker run -d -p 11500:11500 --env NEWS_API_KEY=YOUR_NEWS_API_KEY '$IMAGE_ID'"
    
    echo "2. 查看运行中的容器："
    echo "   docker ps"
    
    echo "3. 查看容器日志："
    echo "   docker logs <container_id>"
    
    echo "4. 访问服务："
    echo "   API地址: http://localhost:11500"
    echo "   文档地址: http://localhost:11500/docs"
else
    echo "\n❌ Docker镜像构建失败！"
    echo "请检查错误信息并修复问题后重试。"
    exit 1
fi