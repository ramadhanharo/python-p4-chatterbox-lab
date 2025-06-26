import pytest
from app import app
from models import db, Message

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

class TestAppExtended:
    def test_message_creation(self, client):
        """Test message creation"""
        with app.app_context():
            message = Message(
                body="Hello 👋",
                username="tester"
            )
            db.session.add(message)
            db.session.commit()
            
            # Verify message was created
            test_message = Message.query.first()
            assert test_message.body == "Hello 👋"
            assert test_message.username == "tester"
            
            # Clean up
            db.session.delete(test_message)
            db.session.commit()

    def test_get_messages_empty(self, client):
        """Test GET /messages returns empty list when no messages"""
        response = client.get('/messages')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_post_message_valid(self, client):
        """Test POST /messages with valid data"""
        data = {'body': 'Test message', 'username': 'tester'}
        response = client.post('/messages', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['body'] == data['body']
        assert json_data['username'] == data['username']

    def test_post_message_missing_fields(self, client):
        """Test POST /messages with missing fields"""
        data = {'body': 'Test message'}
        response = client.post('/messages', json=data)
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_get_message_by_id(self, client):
        """Test GET /messages/<id>"""
        with app.app_context():
            message = Message(body='Hello', username='tester')
            db.session.add(message)
            db.session.commit()
            message_id = message.id

        response = client.get(f'/messages/{message_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == message_id

    def test_get_message_by_id_not_found(self, client):
        """Test GET /messages/<id> for non-existent message"""
        response = client.get('/messages/9999')
        assert response.status_code == 404
        assert 'error' in response.get_json()

    def test_patch_message_valid(self, client):
        """Test PATCH /messages/<id> with valid data"""
        with app.app_context():
            message = Message(body='Old body', username='tester')
            db.session.add(message)
            db.session.commit()
            message_id = message.id

        data = {'body': 'New body'}
        response = client.patch(f'/messages/{message_id}', json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['body'] == 'New body'

    def test_patch_message_invalid(self, client):
        """Test PATCH /messages/<id> with invalid data"""
        with app.app_context():
            message = Message(body='Old body', username='tester')
            db.session.add(message)
            db.session.commit()
            message_id = message.id

        data = {'body': ''}
        response = client.patch(f'/messages/{message_id}', json=data)
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_patch_message_missing_fields(self, client):
        """Test PATCH /messages/<id> with missing fields"""
        with app.app_context():
            message = Message(body='Old body', username='tester')
            db.session.add(message)
            db.session.commit()
            message_id = message.id

        data = {'invalid_field': 'value'}
        response = client.patch(f'/messages/{message_id}', json=data)
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_delete_message(self, client):
        """Test DELETE /messages/<id>"""
        with app.app_context():
            message = Message(body='To be deleted', username='tester')
            db.session.add(message)
            db.session.commit()
            message_id = message.id

        response = client.delete(f'/messages/{message_id}')
        assert response.status_code == 204

        # Verify deletion
        with app.app_context():
            deleted_message = Message.query.filter_by(id=message_id).first()
            assert deleted_message is None
