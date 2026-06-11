import requests
import logging 

logger = logging.getLogger("app.main")
logging.basicConfig(level='DEBUG')

recommendations_url = 'http://127.0.0.1:8000' 
events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# task 6/6

user_id = 1291250

# 1 - put events for user
event_item_ids =  [7144, 16299, 5907, 18135]
for event_item_id in event_item_ids:
    params = {"user_id": user_id, "item_id": event_item_id}

    resp = requests.post(events_store_url + "/put", headers=headers, params=params)
    
    if resp.status_code == 200:
        result = resp.json()
    else:
        result = None
        print(f"status code: {resp.status_code}")
        
    print(result)                 

# 2 - Получим 10 рекомендаций каждого типа для данного пользователя:

params = {"user_id": user_id, 'k': 10}
resp_offline = requests.post(recommendations_url + "/recommendations_offline", headers=headers, params=params)
resp_online = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
resp_blended = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)

recs_offline = resp_offline.json()["recs"]
recs_online = resp_online.json()["recs"]
recs_blended = resp_blended.json()["recs"]

print('recs_offline', recs_offline)
print('recs_online', recs_online)
print('recs_blended', recs_blended) 

#-------
import pandas as pd
items = pd.read_parquet("data/preprocess/items.par")

# Показать рекомендации
def display_items(item_ids):

    item_columns_to_use = ["item_id", "author", "title", "genre_and_votes", "average_rating", "ratings_count"]
    
    items_selected = items.query("item_id in @item_ids")[item_columns_to_use]
    items_selected = items_selected.set_index("item_id").reindex(item_ids)
    items_selected = items_selected.reset_index()
    
    print(items_selected)
    
print("Онлайн-события")
display_items(event_item_ids)
print("Офлайн-рекомендации")
display_items(recs_offline)
print("Онлайн-рекомендации")
display_items(recs_online)
print("Рекомендации")
display_items(recs_blended) 
