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
import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

"""
| Biblioteca       | Pra que serve              |
| ---------------- | -------------------------- |
| FastAPI          | Criar a API                |
| FastAPI Security | Autenticação               |
| Pydantic         | Validação de dados         |
| typing           | Tipagem (Python padrão)    |
| secrets          | Segurança (tokens, senhas) |
| os               | Sistema operacional        |
| SQLAlchemy       | Banco de dados (ORM)       |

"""

DATABASE_URL = os.getenv("DATABASE_URL") # Aqui é a url do banco de dados

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Cria a conexão com o banco de dados usando a URL informada.
# O "check_same_thread=False" permite que o SQLite seja usado em múltiplas threads (necessário em APIs como FastAPI).

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Cria uma fábrica de sessões (Session) para interagir com o banco.
# autocommit=False: você controla quando salvar (commit).
# autoflush=False: evita enviar alterações automaticamente antes de consultas.
# bind=engine: conecta essa sessão ao banco criado acima.

Base = declarative_base()
# Base usada para criar os modelos (tabelas) do banco de dados com ORM.
# Todas as classes de modelo irão herdar dessa Base.

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar uma coleção de livros",
    version="1.0.0",
    contact={
        "name":"Gabriel Martins",
        "email":"gabrieuz.martins@gmail.com"
    }
)

# Variáveis de ambiente, ficam no arquivo .env
MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")
security = HTTPBasic()

class LivroDB(Base):
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
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )

@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    # esse db é a conexão com o banco de dados.
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limit estão com valores inválidos")
    
    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    """
    db.query(LivroDB)
        → Busca todos os registros da tabela/modelo LivroDB.

    .offset((page - 1) * limit)
        → Pula uma quantidade de registros com base na página atual.
        Exemplo:

        page = 1 → offset = 0 (não pula nada)
        page = 2 → offset = limit (pula os primeiros registros)

        .limit(limit)
            → Limita a quantidade de resultados retornados (ex: 10 por página).

        .all()
            → Executa a consulta e retorna os resultados em lista.
    """

    if not livros:
        return {"message": "Nenhum livro cadastrado"}

    
    total_livros = db.query(LivroDB).count()
    # Esse codigo é para contar a quantidade total de livros cadastrados no banco de dados, para que eu possa retornar essa informação na resposta da minha API, 
    # e também para que eu possa usar essa informação para calcular a quantidade total de páginas disponíveis, caso eu queira implementar uma funcionalidade de paginação mais avançada no futuro.

    return{
        "page": page,
        "limit": limit,
        "total_livros": total_livros,
        "livros": [{"id": livro.id, "nome_livro": livro.nome_livro, "autor_livro": livro.autor_livro, "ano_livro": livro.ano_livro} for livro in livros]
    }
    # Aqui eu retorno um dicionário com as informações da página, limite, total de livros 
    # e a lista de livros paginados (com as informações estruturadas em um dicionário para cada livro)
   
@app.post("/livros")
def post_livros(livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    # esse db é a conexão com o banco de dados.
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro, LivroDB.ano_livro == livro.ano_livro).first()
    # Aqui eu verifico se já existe um livro com as mesmas informações (nome, autor e ano) no banco de dados, para evitar duplicidade de registros.

    if db_livro:
        raise HTTPException(status_code=400, detail="Livro já cadastrado")
    
    novo_livro = LivroDB(nome_livro = livro.nome_livro, autor_livro = livro.autor_livro, ano_livro = livro.ano_livro)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro) # Aqui eu atualizo o objeto novo_livro com as informações do banco de dados, como o id gerado automaticamente pelo banco de dados.

    return {"message": f"Livro {novo_livro.nome_livro} adicionado com sucesso!"}

@app.put("/livros/{id_livro}")
def put_livros(id_livro: int, livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    # esse db é a conexão com o banco de dados.
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    # coenxão especificamente com uma tabela do banco de dados, no caso a tabela livros, e eu filtro essa tabela para encontrar o livro com o id fornecido na URL da requisição, e depois eu pego o primeiro resultado encontrado (que deve ser o único resultado, já que o id é único).
    # Aqui eu verifico se existe um livro com o id fornecido no banco de dados, para que eu possa atualizar as informações desse livro.
    
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro
    db.commit()
    db.refresh(db_livro)

    return {"message": "Livro atualizado com sucesso!"}

    # Aqui eu atualizo as informações do livro encontrado no banco de dados com as novas informações fornecidas no corpo da requisição, e depois eu salvo as alterações no banco de dados com o commit().

@app.delete("/livros/{id_livro}")
def delete_livro(id_livro: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(db_livro)
    db.commit()

    return {"message": f"Livro {db_livro.nome_livro} deletado com sucesso!"}

# http://127.0.0.1:8000/livros?page=1&limit=100
# aqui eu escolho a página e a quantidade de livros que eu quero ver por página

# ORM - Object Relational Mapping - é uma técnica de programação que permite que os desenvolvedores trabalhem com bancos de dados relacionais usando objetos em vez de escrever consultas SQL diretamente.
# FastAPI / Django / Flask / Node / Express / Nest.js / Laravel / Spring Boot -> Frameworks Backends todos possuem suporte a ORM.
# Vantagens -> A gente vai ganhar agilidade no desenvolvimento
# Desvantagens -> A gente pode perder performance no Banco de Dados