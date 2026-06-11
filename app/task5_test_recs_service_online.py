import requests
import logging 

logger = logging.getLogger("app.main")
logging.basicConfig(level='DEBUG')

recommendations_url = 'http://127.0.0.1:8000' 
events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# task 5/6
user_id = 1291248

# 1 - put events for user
event_item_ids = [41899, 102868, 5472, 5907]
for event_item_id in event_item_ids:
    params = {"user_id": 1291248, "item_id": event_item_id}

    resp = requests.post(events_store_url + "/put", headers=headers, params=params)
    
    if resp.status_code == 200:
        result = resp.json()
    else:
        result = None
        print(f"status code: {resp.status_code}")
        
    print(result)
                       
# 2 - get online recs for last objects
params = {"user_id": user_id, 'k': 5}
logger.info(f'call service, params: {params}')

resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
    
if resp.status_code == 200:
    online_recs = resp.json()
else:
    online_recs = []
    print(f"status code: {resp.status_code}")
    print(f"message: {resp.json()}")

print(online_recs) 


