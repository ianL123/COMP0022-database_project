FROM python:3.9-slim
WORKDIR /app
RUN pip install flask flask-sqlalchemy pymysql cryptography
COPY . .
CMD ["python", "app.py"]