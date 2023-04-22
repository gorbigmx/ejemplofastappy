import requests

url = 'http://127.0.0.1:8000/token'

headers = {
    'Content-type': 'application/x-www-form-urlencoded'
}

params = {
    'usernamef': 'juan',
    'passwordf': 'formulario',
}

r = requests.post(url, headers=headers, data=params)

print(f'Status http: {r.status_code}')

print(f'Response: {r.json()}')