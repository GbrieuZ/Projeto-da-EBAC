# API de Livros

# GET, POST, PUT e DELETE

# GET - Buscar os dados dos livros (Create)
# POST - Adicionar novos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - Deletar informações dos livros (Delete)

# Vamos acessar nosso ENDPOINT
# E vamos acessar os PATH's desse endpoint
# Query Strings

#CRUD - Create, Read, Update, Delete

# Documentação Swagger - Documentar os endpoints da nossa API (aplicação)

# Acesse minha documentação swagger: http://127.0.0.1:8000/docs#/

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./livros.db" # Aqui é a url do banco de dados

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Esse codigo é para usar localmente o banco de dados
# Para uso normal, precisaria de um user, senha, host, porta e nome do banco de dados.


app = FastAPI(
    title="API de Livros",
    description="API para gerenciar uma coleção de livros",
    version="1.0.0",
    contact={
        "name":"Gabriel Martins",
        "email":"gabrieuz.martins@gmail.com"
    }
)

MEU_USUARIO = "admin" 
MIHA_SENHA = "admin"

security = HTTPBasic()

meus_livrozinhos = {}

class Livro(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True) # primary_key=True é para dizer que essa coluna é a chave primária do banco de dados, ou seja, o identificador único de cada registro
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine) # Aqui eu crio as tabelas do banco de dados, ou seja, a tabela livros com as colunas id, nome_livro, autor_livro e ano_livro


def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MIHA_SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10,credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limit estão com valores inválidos")
    if not meus_livrozinhos:
        return {"message": "Nenhum livro cadastrado"}
    
    start = (page-1) * limit
    end = start + limit

    livros_paginados = [
        {"id": id_livro, "nome_livro": livro_data ["nome_livro"], "autor_livro": livro_data["autor_livro"], "ano_livro": livro_data["ano_livro"]}
        for id_livro, livro_data in list(meus_livrozinhos.items())[start:end]
        #for loop dentro dos meus_livrozinhos, onde eu estruturo as info dentro de uma lista (transformo em lista)
        #Dando for loop para pegar o id_livro e livro_data usando a paginação estruturada pelo start e end
        #Ao mesmo tempo eu crio um dicionário com as informações que eu quero retornar
    ]
    
    return{
        "page": page,
        "limit": limit,
        "total_livros": len(meus_livrozinhos),
        "livros": livros_paginados
    }
# Essa função mostratrá os livros cadastrados na minha API de forma paginada como no retorno acima

# http://127.0.0.1:8000/livros?page=1&limit=100
# aqui eu escolho a página e a quantidade de livros que eu quero ver por página

    
# id do livro
# nome do livro
# autor do livro
# ano de publicação

@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro in meus_livrozinhos:
        raise HTTPException(status_code=400, detail="Livro já cadastrado")
    else:
        meus_livrozinhos[id_livro] = livro.dict()
        return {"message": "Livro adicionado com sucesso!"}
    

@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    meu_livro = meus_livrozinhos.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        # Eu jogo essa informação dentro do meu antigo dicionário (que é o meus_livrozinhos)
        # E NÃOooooo dentro da REFERENCIA do antigo dicionário
        # Antigo dicionário != Referencia do antigo dicionário
        meus_livrozinhos[id_livro] = livro.dict() 
        
        
        return {"message": "Livro atualizado com sucesso!"}
    
@app.delete("/deletar/{id_livro}")
def delet_livro(id_livro: int, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro not in meus_livrozinhos:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del meus_livrozinhos[id_livro]
        return {"message": "Livro deletado com sucesso!"}