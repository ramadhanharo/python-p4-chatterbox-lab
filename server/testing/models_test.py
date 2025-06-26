import pytest
from models import Message, db
from datetime import datetime

def test_message_creation(client, message_data):
    """Test message model creation"""
    with client.application.app_context():
        # Test valid creation
        message = Message(**message_data)
        db.session.add(message)
        db.session.commit()
        
        assert message.id is not None
        assert message.body == message_data['body']
        assert message.username == message_data['username']
        assert isinstance(message.created_at, datetime)

def test_message_required_fields(client):
    """Test message model required fields"""
    with client.application.app_context():
        # Test missing body
        message = Message(username="testuser")
        db.session.add(message)
        with pytest.raises(Exception):
            db.session.commit()
        
        # Test missing username
        message = Message(body="Test message")
        db.session.add(message)
        with pytest.raises(Exception):
            db.session.commit()

def test_message_serialization(client):
    """Test message serialization with to_dict()"""
    with client.application.app_context():
        message = Message.query.first()
        message_dict = message.to_dict()
        
        assert isinstance(message_dict, dict)
        assert message_dict['id'] == message.id
        assert message_dict['body'] == message.body
        assert message_dict['username'] == message.username
        assert 'created_at' in message_dict
        assert isinstance(message_dict['created_at'], str)

def test_message_ordering(client):
    """Test message ordering by created_at"""
    with client.application.app_context():
        messages = Message.query.order_by(Message.created_at.asc()).all()
        assert len(messages) == 3
        for i in range(len(messages)-1):
            assert messages[i].created_at <= messages[i+1].created_at