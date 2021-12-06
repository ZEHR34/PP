import requests
from requests.auth import HTTPBasicAuth


r = requests.post('http://localhost:5000/user', json={'username': 'test2', 'firstName': 'Name', 'lastName': 'Surname', 'email': 'test@132.com', 'password': 'Test', 'phone': '0987876563'})
print(r.text)

r = requests.get('http://localhost:5000/user/1', auth=HTTPBasicAuth('test1', 'Test'))
print(r.text)

r = requests.get('http://localhost:5000/user/2', auth=HTTPBasicAuth('test1', 'Test'))
print(r.text)

r = requests.delete('http://localhost:5000/user/3', auth=HTTPBasicAuth('test1', 'Test'))
print(r.text)

r = requests.post('http://localhost:5000/wallet', json={'value': '100', 'privacy': True}, auth=HTTPBasicAuth('test', 'Test'))
print(r.text)

r = requests.get('http://localhost:5000/wallet/1', auth=HTTPBasicAuth('test1', 'Test'))
print(r.text)

r = requests.get('http://localhost:5000/wallet/1', auth=HTTPBasicAuth('test', 'Test'))
print(r.text)
