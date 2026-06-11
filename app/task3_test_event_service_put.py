import requests

events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#params = {"user_id": 1337055, "item_id": 17245}

# Задание:
#   Проверьте, что для пользователя 1127794 в Event Store нет никаких событий. 
#   Затем сохраните для этого пользователя последовательно четыре события 
#   с объектами: 18734992, 18734992, 7785, 4731479.
#params = {"user_id": 1127794, "item_id": 18734992}
#params = {"user_id": 1127794, "item_id": 18734992}
#params = {"user_id": 1127794, "item_id": 7785}
#params = {"user_id": 1127794, "item_id": 4731479}

# task 4/6
params = {"user_id": 1291248, "item_id": 17245}

resp = requests.post(events_store_url + "/put", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
    
print(result)