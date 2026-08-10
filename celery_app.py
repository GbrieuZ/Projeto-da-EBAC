from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega o .env quando o worker roda fora do container.

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

celery_app = Celery(
    "tarefas_livros",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"],  # garante que o worker carregue/registre as tarefas de tasks.py
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    result_persistent=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # A API publica e o worker consome na MESMA fila ("livros").
    task_default_queue="livros",
    task_routes={
        "tasks.somar": {"queue": "livros"},
        "tasks.fatorial": {"queue": "livros"},
    },
)
