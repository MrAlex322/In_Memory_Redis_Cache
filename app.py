from flask import Flask, request, jsonify
from cachetools import TTLCache
import time
from cache_manager import register_cache_atexit
from auth import login, requires_auth, load_token, authenticated_users, save_token, verify_token

app = Flask(__name__)
cache = TTLCache(maxsize=100, ttl=60)
register_cache_atexit(cache)


@app.route('/api/login', methods=['POST'])
def login_handler():
    data = request.get_json()
    response, status_code = login(data)
    token = response.json.get('token')
    if token:
        save_token(token)
    return response, status_code


@app.route('/api/protected', methods=['GET'])
@requires_auth
def protected_handler(username):
    return jsonify({'message': f'Hello, {username}! This is a protected route.'}), 200


@app.route('/api/get', methods=['GET'])
def get_handler():
    key = request.args.get('key')
    value = cache.get(key)
    if value is not None:
        return jsonify({'key': key, 'value': value[0]})
    return jsonify({'error': 'Key not found'}), 404


@app.route('/api/set', methods=['POST'])
def set_handler():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    ttl = data.get('ttl')
    if ttl is not None and (not isinstance(ttl, (int, float)) or ttl <= 0):
        return jsonify({'error': 'TTL should be a positive number'}), 400

    expiration_time = None
    if ttl is not None:
        expiration_time = time.time() + ttl

    cache[key] = (value, expiration_time)

    return jsonify({'key': key, 'value': value, 'ttl': ttl})


@app.route('/api/del', methods=['DELETE'])
def delete_handler():
    key = request.args.get('key')
    if key in cache:
        del cache[key]
        return jsonify({'message': 'Key deleted'})
    return jsonify({'error': 'Key not found'}), 404


@app.route('/api/keys', methods=['GET'])
def keys_handler():
    keys = list(cache.keys())
    return jsonify({'keys': keys})


@app.route('/api/hget', methods=['GET'])
def hget_handler():
    key = request.args.get('key')
    field = request.args.get('field')
    value = cache.get(key, {}).get(field)
    if value is not None:
        return jsonify({'key': key, 'field': field, 'value': value})
    return jsonify({'error': 'Key or field not found'}), 404


@app.route('/api/hset', methods=['POST'])
def hset_handler():
    data = request.get_json()
    key = data.get('key')
    field = data.get('field')
    value = data.get('value')

    hash_data = cache.get(key, {})
    hash_data[field] = value
    cache[key] = hash_data
    return jsonify({'key': key, 'field': field, 'value': value})


@app.route('/api/lget', methods=['GET'])
def lget_handler():
    key = request.args.get('key')
    index = int(request.args.get('index', -1))
    list_data = cache.get(key, [])

    if 0 <= index < len(list_data):
        value = list_data[index]
        return jsonify({'key': key, 'index': index, 'value': value})
    else:
        return jsonify({'error': 'Key or index not found'}), 404


@app.route('/api/lset', methods=['POST'])
def lset_handler():
    data = request.get_json()
    key = data.get('key')
    index = int(data.get('index', -1))
    value = data.get('value')

    list_data = cache.get(key, [])
    if index < 0:
        list_data.append(value)
    else:
        list_data[index] = value
    cache[key] = list_data
    return jsonify({'key': key, 'index': index, 'value': value})


if __name__ == '__main__':
    token = load_token()
    if token:
        username = verify_token(token)
        if username:
            authenticated_users.add(username)
    app.run()
