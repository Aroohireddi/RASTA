FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN mkdir -p data/raw
EXPOSE 8001
CMD ["python", "src/main.py"]