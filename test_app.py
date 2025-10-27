import pytest
import json
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Sử dụng file test riêng cho testing
    app.config['DATA_FILE'] = 'data/test_tasks.json'
    
    # Đảm bảo thư mục data tồn tại
    os.makedirs('data', exist_ok=True)
    
    # Tạo file test rỗng trước mỗi test
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump([], f)
        
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test trang chủ load thành công và hiển thị đúng tiêu đề"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Project Task Tracker" in rv.data

def test_about_page(client):
    """Test trang about load thành công"""
    rv = client.get('/about')
    assert rv.status_code == 200

def test_health_check(client):
    """Test API health check trả về status OK và version"""
    rv = client.get('/api/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'healthy'
    assert 'version' in json_data
    assert 'environment' in json_data

def test_create_task(client):
    """Test tạo task mới"""
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['title'] == 'Test Task'
    assert json_data['status'] == 'pending'
    assert 'id' in json_data
    assert 'created_at' in json_data

def test_get_tasks(client):
    """Test lấy danh sách tasks"""
    # Tạo task test
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
    # Get tasks
    rv = client.get('/api/tasks')
    assert rv.status_code == 200
    tasks = rv.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'

def test_update_task_status(client):
    """Test cập nhật trạng thái task"""
    # Tạo task
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    task_id = rv.get_json()['id']
    
    # Cập nhật status
    update_data = {'status': 'completed'}
    rv = client.put(f'/api/tasks/{task_id}',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'completed'

def test_task_validation(client):
    """Test validation khi tạo task"""
    # Test missing required fields
    task_data = {'title': 'Test Task'}
    rv = client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 400

def test_invalid_task_id(client):
    """Test xử lý task ID không tồn tại"""
    update_data = {'status': 'completed'}
    rv = client.put('/api/tasks/invalid_id',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 404

def test_data_persistence(client):
    """Test dữ liệu được lưu trữ đúng"""
    # Tạo task
    task_data = {
        'title': 'Persistence Test',
        'description': 'Test Description',
        'priority': 'high'
    }
    client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
    # Kiểm tra file có tồn tại
    assert os.path.exists(app.config['DATA_FILE'])
    
    # Đọc file và verify nội dung
    with open(app.config['DATA_FILE'], 'r') as f:
        tasks = json.load(f)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Persistence Test'
