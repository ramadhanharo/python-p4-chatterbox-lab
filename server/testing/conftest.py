import pytest
from app import create_app, db
from models import Message
from datetime import datetime, timedelta

@pytest.fixture
def client():
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
            # Add comprehensive test data
            now = datetime.utcnow()
            messages = [
                Message(
                    body="Test message 1", 
                    username="user1",
                    created_at=now - timedelta(minutes=5)
                ),
                Message(
                    body="Test message 2", 
                    username="user2",
                    created_at=now - timedelta(minutes=2)
                ),
                Message(
                    body="Test message 3",
                    username="user3",
                    created_at=now
                )
            ]
            db.session.add_all(messages)
            db.session.commit()
        yield client
        with test_app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def message_data():
    return {
        "body": "Test message body",
        "username": "testuser"
    }
