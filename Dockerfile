# Imagem docker
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

# Windows - choco install podman-cli
# pip install podman-compose

# Para rodar o projeto, basta usar o comando:
# podman machine start
# podman-compose build
# podman-compose up --build ate aq pra executar dps de buildar

# podman build -t projeto-ebac . 
# aqui vai passar por todos os passos para ver se esta correto
# para executar - podman run --env-file .env -d -p 8000:8000 projeto-ebac

#SEGURANÇA

# Use imagens oficiais e verificadas
# Use imagenns pequenas e minimalistas
# Atualize regularmente as imagens
# Não armazenar senhgas e credenciais dentro do container
# Remova containers e imagens não utilizados
# Desative privilegios desnecessários
# Monitore os logs e o comportamento do container