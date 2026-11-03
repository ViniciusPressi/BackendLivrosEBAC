# API DE LIVROS

#POST - adicionar livros (Create)
#GET- buscar dados dos livros (Read)
#PUT - atualizar info dos livros (Update)
# DELETE - Deletar info (Delete)
#CRUD
#poetry init
#poetry add fastapi
#poetry run fastapi dev "arquivo"
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os

from sqlalchemy import create_engine, Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros",
    version="1.0.0",
    contact={"name":"Vinicius", "email":"xxxx@gmail.com"}
)

meu_usuario = "admin"
minha_senha= "admin"

security = HTTPBasic()

meus_livros = {}

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct= secrets.compare_digest(credentials.password, minha_senha)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate" : "Basic"}
        )
            
        

class LivroDB(Base):
   __tablename__ = "Livros"
   id = Column(Integer,primary_key=True, index=True)
   nome = Column(String, index=True)
   autor = Column(String, index=True)
   ano = Column(Integer)

class Livro(BaseModel):
    nome: str
    autor: str
    ano: int 

Base.metadata.create_all(bind = engine)

def sessao_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close
    
@app.get("/livros")
def get_livros( page: int = 1, limit: int = 10, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials= Depends(autenticar_usuario)):
   if page < 1 or limit <1: 
       raise HTTPException(status_code=400, detail="Page ou limit inválidos!")

   livros = db.query(LivroDB).offset((page-1)*limit).limit(limit).all() #pega dados na paginação correta
   
   if not livros:
    return {"message": "Não existe nenhum livro!"}

   total = db.query(LivroDB).count()
   livro_array = [{"id": livro.id, "nome": livro.nome, "autor": livro.autor, "ano" : livro.ano} for livro in livros]
   return{
       "page": page,
       "limit": limit,
       "total": total,
       "livros":  livro_array
   }

# id, nome, autor, ano de lançamento
@app.post("/adicionar")
def post_livros( livro: Livro,db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(security)):
    db_livro = db.query(LivroDB).filter(LivroDB.nome==livro.nome, LivroDB.autor == livro.autor).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Esse livro já existe no banco de dados.")

    novo_livro = LivroDB(nome = livro.nome, autor = livro.autor, ano = livro.ano) 
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {"message" : "Livro adicionado com sucesso!"}

@app.put("/atualizar/{id}")
def put_livros(id: int, livro: Livro,db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(security)):
    db_livro = db.query(LivroDB).filter(LivroDB.id==id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado no banco de dados.")

    db_livro.nome = livro.nome
    db_livro.autor = livro.autor
    db_livro.ano = livro.ano

    db.commit()
    db.refresh(db_livro)

    return {"message" : "Livro atualizado com sucesso!"}

@app.delete("/deletar/{id}")
def delete_livro(id: int,db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(security)):
    db_livro = db.query(LivroDB).filter(LivroDB.id==id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado no banco de dados.")

    db.delete(db_livro)
    db.commit()
    return {"message": "Livro deletado com sucesso!"}