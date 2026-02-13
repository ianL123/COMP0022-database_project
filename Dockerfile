FROM python:3.9-slim
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt
COPY . .
# Install the listed libraries
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
CMD ["python", "app.py"]