FROM python:3.8-slim
WORKDIR /app
COPY . .
EXPOSE 8889
RUN pip3 install cos-python-sdk-v5 jinja2 aioredis requests beautifulsoup4  fastapi uvicorn[standard] lxml -i https://mirrors.cloud.tencent.com/pypi/simple
ENV REDIS_HOST 127.0.0.1
ENV REDIS_PORT 6379
ENV SECRET_ID "server_id"
ENV SECRET_KEY "server_key"
ENV REGION "ap-guangzhou"
ENV BUCKET "bucket_name"
ENV CDNURL "https://example.com/"
CMD uvicorn main:app --host 0.0.0.0 --port 8889