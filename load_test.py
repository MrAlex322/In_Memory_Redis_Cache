from locust import HttpUser, task, between


class MyUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    @task
    def login(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            'username': 'user',
            'password': 'pass'
        }
        response = self.client.post('/api/login', json=data, headers=headers)
        if response.status_code == 200:
            self.token = response.json()['token']
        else:
            self.token = None

    @task
    def get_protected(self):
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            self.client.get('/api/protected', headers=headers)

    @task
    def get_key(self):
        key = 'my_key'
        self.client.get(f'/api/get?key={key}')
