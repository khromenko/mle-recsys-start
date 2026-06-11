import requests
import logging 

logger = logging.getLogger("app.main")
logging.basicConfig(level='DEBUG')

recommendations_url = 'http://127.0.0.1:8000' 

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1291248, 'k': 3}

logger.info(f'call service, params: {params}')

resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)

if resp.status_code == 200:
    online_recs = resp.json()
else:
    online_recs = []
    print(f"status code: {resp.status_code}")
    print(f"message: {resp.json()}")

print(online_recs) 

