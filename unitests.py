import unittest
import json
from app import app, cache


class TestApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_key_exists(self):
        cache["test_key"] = ("test_value", None)

        response = self.app.get('/api/get?key=test_key')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['key'], 'test_key')
        self.assertEqual(data['value'], 'test_value')

    def test_get_key_not_found(self):
        response = self.app.get('/api/get?key=non_existent_key')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Key not found')

    def test_set_key_with_ttl(self):
        data = {
            "key": "new_key",
            "value": "new_value",
            "ttl": 30
        }

        response = self.app.post('/api/set', json=data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['key'], 'new_key')
        self.assertEqual(data['value'], 'new_value')
        self.assertEqual(data['ttl'], 30)

        self.assertIn('new_key', cache)
        self.assertEqual(cache['new_key'][0], 'new_value')

        self.assertTrue(cache['new_key'][1] is not None)

    def test_del_key_exists(self):
        cache["test_key"] = ("test_value", None)

        response = self.app.delete('/api/del?key=test_key')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Key deleted')

        self.assertNotIn('test_key', cache)

    def test_del_key_not_found(self):
        response = self.app.delete('/api/del?key=non_existent_key')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Key not found')

    def test_hget_key_exists(self):
        cache["test_hash"] = {"field1": "value1", "field2": "value2"}

        response = self.app.get('/api/hget?key=test_hash&field=field1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['key'], 'test_hash')
        self.assertEqual(data['field'], 'field1')
        self.assertEqual(data['value'], 'value1')

    def test_lget_key_not_found(self):
        response = self.app.get('/api/lget?key=non_existent_list&index=0')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Key or index not found')

    def test_hset_existing_key(self):
        cache["existing_hash"] = {"field1": "value1"}

        data = {
            "key": "existing_hash",
            "field": "field2",
            "value": "value2"
        }

        response = self.app.post('/api/hset', json=data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['key'], 'existing_hash')
        self.assertEqual(data['field'], 'field2')
        self.assertEqual(data['value'], 'value2')

        self.assertIn('existing_hash', cache)
        self.assertEqual(cache['existing_hash'], {"field1": "value1", "field2": "value2"})

    def test_lget_key_exists(self):
        cache["test_list"] = ["item1", "item2", "item3"]

        response = self.app.get('/api/lget?key=test_list&index=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['key'], 'test_list')
        self.assertEqual(data['index'], 1)
        self.assertEqual(data['value'], 'item2')


if __name__ == '__main__':
    unittest.main()
