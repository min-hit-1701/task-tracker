import pytest
import json
import os
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Setup test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['DATA_FILE'] = 'data/test_tasks.json'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test user
            user = User(
                username='testuser',
                password=generate_password_hash('testpass'),
                email='test@example.com'
            )
            db.session.add(user)
            db.session.commit()
        yield client
        # Cleanup
        if os.path.exists(app.config['DATA_FILE']):
            os.remove(app.config['DATA_FILE'])
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_client(client):
    """Client with authenticated user"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

def test_login_page(client):
    """Test login page"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'ng nh' in rv.data

def test_login(client):
    """Test login functionality"""
    rv = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert rv.status_code == 302  # Redirect after login

def test_home_page(auth_client):
    """Test trang chủ"""
    rv = auth_client.get('/')
    assert rv.status_code == 200
    assert b"Project Task Tracker" in rv.data

def test_about_page(client):
    """Test trang about"""
    rv = client.get('/about')
    assert rv.status_code == 200

def test_health_check(client):
    """Test API health check"""
    rv = client.get('/api/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'healthy'

def test_create_task(auth_client):
    """Test tạo task mới"""
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = auth_client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['title'] == 'Test Task'

def test_get_tasks(auth_client):
    """Test lấy danh sách tasks"""
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    auth_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
    rv = auth_client.get('/api/tasks')
    assert rv.status_code == 200
    tasks = rv.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'

def test_update_task_status(auth_client):
    """Test cập nhật trạng thái task"""
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high'
    }
    rv = auth_client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    task_id = rv.get_json()['id']
    
    update_data = {'status': 'completed'}
    rv = auth_client.put(f'/api/tasks/{task_id}',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'completed'

def test_task_validation(auth_client):
    """Test validation khi tạo task"""
    task_data = {'title': 'Test Task'}
    rv = auth_client.post('/api/tasks',
                    data=json.dumps(task_data),
                    content_type='application/json')
    assert rv.status_code == 201

def test_invalid_task_id(auth_client):
    """Test xử lý task ID không tồn tại"""
    update_data = {'status': 'completed'}
    rv = auth_client.put('/api/tasks/invalid_id',
                   data=json.dumps(update_data),
                   content_type='application/json')
    assert rv.status_code == 404

def test_data_persistence(auth_client):
    """Test dữ liệu được lưu trữ đúng"""
    task_data = {
        'title': 'Persistence Test',
        'description': 'Test Description',
        'priority': 'high'
    }
    auth_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json')
    
    data_file = app.config['DATA_FILE']
    assert os.path.exists(data_file)
    
    with open(data_file, 'r') as f:
        tasks = json.load(f)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Persistence Test'