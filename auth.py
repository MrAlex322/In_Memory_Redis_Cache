import jwt
import os
import json
from flask import jsonify

SECRET_KEY = 'fbbfflfbl8fl9flf8qdq9'
TOKEN_FILE = 'token.json'
authenticated_users = set()


def generate_token(username):
    token = jwt.encode({'username': username}, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_token['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token}, f)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data.get('token')
            except json.JSONDecodeError:
                pass
    return None


def login(data):
    username = data.get('username')
    password = data.get('password')

    if username == 'user' and password == 'pass':
        token = generate_token(username)
        authenticated_users.add(username)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


def requires_auth(f):
    def decorated(*args, **kwargs):
        token = kwargs.get('token')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        username = verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid token'}), 401

        kwargs['username'] = username
        return f(*args, **kwargs)

    return decorated
