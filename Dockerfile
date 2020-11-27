FROM python:3.8-slim
WORKDIR /app
COPY . .
EXPOSE 8999
RUN pip3 install -r requirements.txt
CMD uvicorn test:app --port 8889