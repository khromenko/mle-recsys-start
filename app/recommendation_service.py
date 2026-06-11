import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from requests.exceptions import ConnectionError
from contextlib import asynccontextmanager
from app.Recommendations import Recommendations

"""
Сервис рекомендаций - оффлайн /recommendations и онлайн - /recommendations_online

Запуск сервиса на порту 8000:
uvicorn app.recommendation_service:app --port 8000
"""


logger = logging.getLogger("uvicorn.error")
rec_store = Recommendations()

features_store_url = "http://127.0.0.1:8010/similar_items"
events_store_url = "http://127.0.0.1:8020/get"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    
    rec_store.load(
        "personal",
        "data/final-recs-with-features/final_recommendations_feat.parquet", # ваш код здесь #
        columns=["user_id", "item_id", "rank"],
    )
    rec_store.load(
        "default",
        "top_recs.parquet", # ваш код здесь #,
        columns=["item_id", "rank"],
    )
    
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")
    
# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
    logger.info(f'recommendations_offline() user_id: {user_id}, k: {k}')    

    recs = rec_store.get(user_id, k)
    return {"recs": recs}

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids

@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    logger.info(f'recommendations_online() user_id: {user_id}, k: {k}')

    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    
    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": k}

    try:
        resp = requests.post(events_store_url, headers=headers, params=params)
    except ConnectionError as e:
        logger.error(e)
        return JSONResponse(
            status_code=503,
            content={"error": f"{e} while calling event service url - {events_store_url}"},
        )    
    
    events = resp.json()
    events = events["events"]

    logger.info(f'got user events: {events}')

    # получаем список похожих объектов
    if len(events) > 0:

        # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
        items = []
        scores = []
        for item_id in events:
            # для каждого item_id получаем список похожих в item_similar_items
            # ваш код здесь

            params = {"item_id": item_id, "k": k}
            try:
                resp = requests.post(features_store_url, headers=headers, params=params) 
            except ConnectionError as e:
                logger.error(e)
                return JSONResponse(
                    status_code=503,
                    content={"error": f"{e} while calling feature service url - {features_store_url}"},
                )           
            
            item_similar_items = resp.json()
            #logger.info(f'for item_id = {item_id} got similar items: {item_similar_items}')

            if len(item_similar_items) > 0:
                items += item_similar_items["item_id_2"]
                scores += item_similar_items["score"]
            
        # сортируем похожие объекты по scores в убывающем порядке
        # для старта это приемлемый подход
        combined = list(zip(items, scores))
        combined = sorted(combined, key=lambda x: x[1], reverse=True)
        combined = [item for item, _ in combined]

        # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
        recs = dedup_ids(combined)
        
    else:
        recs = []

    #logger.info(f'online result recs: {recs}')

    return {"recs": recs}

@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    logger.info(f'recommendations() user_id: {user_id}, k: {k}')

    recs_offline = await recommendations_offline(user_id, k)
    logger.info(f'done recs_offline: {recs_offline}')

    recs_online = await recommendations_online(user_id, k)
    logger.info(f'done recs_online: {recs_online}')

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        # ваш код здесь #
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    # ваш код здесь #
    if len(recs_offline) > min_length:
        recs_blended += recs_offline[min_length:]
    else:
        recs_blended += recs_online[min_length:]

    #logger.info(f'recs before dedup: {recs_blended}')

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)
    
    # оставляем только первые k рекомендаций
    # ваш код здесь #
    recs_blended = recs_blended[:k]
    logger.info(f'done recs: {recs_blended}')

    return {"recs": recs_blended}