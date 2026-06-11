import logging
from fastapi import FastAPI

"""
Сервис предоставляет хранилище для добавления - /put, и получения - /get, событий по пользователю и объекту

Запуск сервиса на порту 8020:
uvicorn app.events_service:app --port 8020
"""

logger = logging.getLogger("uvicorn.error")

class EventStore:

    def __init__(self, max_events_per_user=10):

        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, item_id):
        """
        Сохраняет событие
        """

        user_events = self.events[user_id] if user_id in self.events.keys() else []   # ваш код здесь #
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        user_events = self.events[user_id] if user_id in self.events.keys() else [] # ваш код здесь #
        user_events = user_events[:k]

        return user_events

events_store = EventStore() # ваш код здесь #

# создаём приложение FastAPI
app = FastAPI(title="events")

@app.post("/put")
async def put(user_id: int, item_id: int):
    """
    Сохраняет событие для user_id, item_id
    """

    events_store.put(user_id, item_id)

    return {"result": "ok"}

@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """

    events = events_store.get(user_id, k)

    return {"events": events}