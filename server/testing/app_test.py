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

class TestApp:
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