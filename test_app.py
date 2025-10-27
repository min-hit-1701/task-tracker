import pytest
import json
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Sử dụng file test riêng cho testing
    app.config['DATA_FILE'] = 'data/test_tasks.json'
    
    # Đảm bảo file test rỗng trước mỗi test
    os.makedirs('data', exist_ok=True)
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump([], f)
        
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test trang chủ trả về HTTP 200"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Project Task Tracker" in rv.data

def test_about_page(client):
    """Test trang about trả về HTTP 200"""
    rv = client.get('/about')
    assert rv.status_code == 200
    assert b"Trang Gi" in rv.data

def test_health_check(client):
    """Test API health check"""
    rv = client.get('/api/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'healthy'
    assert 'version' in json_data
    assert 'tasks_count' in json_data

def test_create_and_get_task(client):
    """Test tạo và lấy task"""
    # Tạo task mới
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = client.post('/api/tasks', 
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 201
    
    # Kiểm tra task đã được tạo
    rv = client.get('/api/tasks')
    tasks = rv.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'
    assert tasks[0]['status'] == 'pending'

def test_update_task_status(client):
    """Test cập nhật trạng thái task"""
    # Tạo task mới
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = client.post('/api/tasks', 
                    data=json.dumps(task_data),
                    content_type='application/json')
    task_id = rv.get_json()['id']
    
    # Cập nhật trạng thái
    update_data = {'status': 'completed'}
    rv = client.put(f'/api/tasks/{task_id}',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'completed'