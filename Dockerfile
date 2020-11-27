FROM python:3.8-slim
WORKDIR /app
COPY . .
EXPOSE 8999
RUN pip3 install -r requirements.txt && pip3 install uvicorn lxml
CMD uvicorn main:app --port 8889