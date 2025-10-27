from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Đường dẫn file data mặc định
DEFAULT_DATA_FILE = 'data/tasks.json'

def get_data_file():
    """Lấy đường dẫn file data dựa trên environment"""
    return app.config.get('DATA_FILE', DEFAULT_DATA_FILE)

def load_tasks():
    """Load tasks từ file"""
    data_file = get_data_file()
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Lưu tasks vào file"""
    data_file = get_data_file()
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    with open(data_file, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def home():
    return render_template('index.html', tasks=load_tasks())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(load_tasks())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    task = request.get_json()
    tasks = load_tasks()
    
    # Tạo task mới
    new_task = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'title': task.get('title'),
        'description': task.get('description', ''),
        'status': 'pending',
        'priority': task.get('priority', 'medium'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    task_update = request.get_json()
    
    for task in tasks:
        if task['id'] == task_id:
            task.update(task_update)
            save_tasks(tasks)
            return jsonify(task)
            
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)