FROM python:3.8-slim
WORKDIR /app
COPY . .
EXPOSE 8889
RUN pip3 install requests beautifulsoup4  fastapi uvicorn[standard] lxml -i https://mirrors.cloud.tencent.com/pypi/simple
CMD uvicorn main:app --host 0.0.0.0 --port 8889