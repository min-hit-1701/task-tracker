import pytest
import json
import os
from app import app

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Fixture để setup và cleanup trước/sau mỗi test"""
    # Setup: Tạo thư mục data và file test
    os.makedirs('data', exist_ok=True)
    test_file = 'data/test_tasks.json'
    
    # Đảm bảo file trống trước mỗi test
    with open(test_file, 'w') as f:
        json.dump([], f)
    
    yield
    
    # Cleanup: Xóa file test sau mỗi test
    if os.path.exists(test_file):
        os.remove(test_file)

@pytest.fixture
def client():
    """Fixture để tạo test client"""
    app.config['TESTING'] = True
    app.config['DATA_FILE'] = 'data/test_tasks.json'
    """Setup test client"""
    # Sử dụng file data riêng cho testing
    test_data_file = 'data/test_tasks.json'
    
    # Đảm bảo thư mục data tồn tại
    os.makedirs(os.path.dirname(test_data_file), exist_ok=True)
    
    # Xóa file cũ nếu tồn tại
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
    
    # Setup test config
    app.config['TESTING'] = True
    app.config['DATA_FILE'] = test_data_file
    
    with app.test_client() as client:
        yield client
    
    # Cleanup sau khi test xong
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_home_page(client):
    """Test trang chủ load thành công và hiển thị đúng tiêu đề"""
    """Test trang chủ"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Project Task Tracker" in rv.data

def test_about_page(client):
    """Test trang about load thành công"""
    """Test trang about"""
    rv = client.get('/about')
    assert rv.status_code == 200

def test_health_check(client):
    """Test API health check"""
    rv = client.get('/api/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'healthy'

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

def test_get_tasks(client):
    """Test lấy danh sách tasks"""
    # Tạo test task
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
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
    
    update_data = {'status': 'completed'}
    rv = client.put(f'/api/tasks/{task_id}',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'completed'

def test_task_validation(client):
    """Test validation khi tạo task"""
    task_data = {'title': 'Test Task'}
    rv = client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 201

def test_invalid_task_id(client):
    """Test xử lý task ID không tồn tại"""
    update_data = {'status': 'completed'}
    rv = client.put('/api/tasks/invalid_id',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 404

def test_data_persistence(client):
    """Test dữ liệu được lưu trữ đúng"""
    task_data = {
        'title': 'Persistence Test',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    
    # Verify file exists
    assert os.path.exists(app.config['DATA_FILE'])
    
    # Read and verify content
    with open(app.config['DATA_FILE'], 'r') as f:
        tasks = json.load(f)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Persistence Test'
    client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
    # Verify file exists
    data_file = app.config['DATA_FILE']
    assert os.path.exists(data_file)
    
    # Read and verify content
    with open(data_file, 'r') as f:
        tasks = json.load(f)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Persistence Test'
