# Day 27: Dockerfile - AI内容创作平台
# 多阶段构建，减小镜像体积

# 阶段1: 构建依赖
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 安装Python依赖
RUN pip install --no-cache-dir -e "."

# 阶段2: 运行环境
FROM python:3.12-slim AS runtime

WORKDIR /app

# 创建非root用户
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --create-home app

# 从builder复制安装的依赖
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY .env.example ./.env

# 设置权限
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 启动命令
CMD ["python", "-m", "content_platform.main"]
