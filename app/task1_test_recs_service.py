import requests
import logging 

logger = logging.getLogger("app.main")
logging.basicConfig(level='DEBUG')

recommendations_url = 'http://127.0.0.1:8000/recommendations' # ваш код здесь #

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1353637, 'k': 3}

logger.info(f'call service, params: {params}')

resp = requests.post(recommendations_url, headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)