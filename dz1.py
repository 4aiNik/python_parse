import json
import requests

user = '4aiNik'
url = 'https://api.github.com/users/' + user + '/repos'

response = requests.get(url)
if (response.status_code == 200):
    json_data = response.json()
    with open('data.json', 'w') as f:
        json.dump(json_data, f)
    for item in json_data:
        print(item['name'])
