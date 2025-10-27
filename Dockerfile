# Sử dụng Python 3.9 slim base image
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements trước để tận dụng cache của Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Tạo thư mục data và phân quyền
RUN mkdir -p data && chmod 777 data

# Expose port 8080
EXPOSE 8080

# Chạy ứng dụng với gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]