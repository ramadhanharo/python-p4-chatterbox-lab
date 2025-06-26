from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by('created_at').all()
        return make_response([message.to_dict() for message in messages], 200)
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            message = Message(
                body=data['body'],
                username=data['username']
            )
            db.session.add(message)
            db.session.commit()
            return make_response(message.to_dict(), 201)
        except KeyError:
            return make_response({'error': 'Missing required fields'}, 400)
        except Exception as e:
            return make_response({'error': str(e)}, 400)


@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return make_response({'error': 'Message not found'}, 404)

    if request.method == 'GET':
        return make_response(message.to_dict(), 200)

    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            if not data or not any(attr in ['body', 'username'] for attr in data):
                return make_response({'error': "must include 'body' or 'username'"}, 400)

            for attr in data:
                if attr in ['body', 'username']:
                    if not data[attr] or not isinstance(data[attr], str):
                        return make_response({'error': 'Invalid value for {}'.format(attr)}, 400)
                    setattr(message, attr, data[attr])
            
            db.session.commit()
            return make_response(message.to_dict(), 200)
        except Exception as e:
            return make_response({'error': str(e)}, 400)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response('', 204)
