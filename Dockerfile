# Aqui é onde vamos "guardar" o nosso backend.
# Nessa "caixinha" para ser executada em qualquer lugar


# Config base para rodar o projeto
FROM python:3.14-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
