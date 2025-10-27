from flask import Flask, render_template, jsonify, request, redirect, url_for
import socket
import json
from datetime import datetime
import os

app = Flask(__name__)

# Config
class Config:
    APP_VERSION = "1.1.0"
    ENVIRONMENT = "development"
    DATA_FILE = "data/tasks.json"

# Đảm bảo thư mục data tồn tại
os.makedirs('data', exist_ok=True)

# Khởi tạo file data nếu chưa tồn tại
if not os.path.exists(Config.DATA_FILE):
    with open(Config.DATA_FILE, 'w') as f:
        json.dump([], f)

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def load_tasks():
    try:
        with open(Config.DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(Config.DATA_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def home():
    tasks = load_tasks()
    system_info = get_system_info()
    return render_template('index.html', 
                         version=Config.APP_VERSION,
                         environment=Config.ENVIRONMENT,
                         system_info=system_info,
                         tasks=tasks)

@app.route('/about')
def about():
    return render_template('about.html', 
                         version=Config.APP_VERSION,
                         environment=Config.ENVIRONMENT)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(load_tasks())

@app.route('/api/tasks', methods=['POST'])
def add_task():
    task = request.json
    task['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
    task['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task['status'] = 'pending'
    
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    
    return jsonify(task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = request.json.get('status', task['status'])
            task['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/health')
def health_check():
    tasks_count = len(load_tasks())
    return jsonify({
        "status": "healthy",
        "version": Config.APP_VERSION,
        "environment": Config.ENVIRONMENT,
        "tasks_count": tasks_count,
        **get_system_info()
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)