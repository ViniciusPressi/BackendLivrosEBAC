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
            
        

class Livro(BaseModel):
    nome: str
    autor: str
    ano: int

@app.get("/livros")
def get_livros( page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials= Depends(autenticar_usuario)):
   if page < 1 or limit <1: 
       raise HTTPException(status_code=400, detail="Page ou limit inválidos!")
   if not meus_livros:
    return {"message": "Não existe nenhum livro!"}
   start = (page -1) * limit
   end = start + limit

   livros_paginados=[
       {
           "id": id, "nome":livro_data["nome"], "autor":livro_data["autor"], "ano":livro_data["ano"]
       }
       for id, livro_data in list(meus_livros.items())[start:end]
   ]
   return{
       "page": page,
       "limit": limit,
       "total":len(meus_livros),
       "livros": livros_paginados
   }

# id, nome, autor, ano de lançamento
@app.post("/adicionar")
def post_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(security)):
    if id in meus_livros:
        raise HTTPException(status_code=400, detail="Esse livro já existe.")
    else:
        meus_livros[id]=livro.model_dump()
        return {"message": "Livro criado com sucesso!"}

@app.put("/atualizar/{id}")
def put_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(security)):
    meu_livro=meus_livros.get(id)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Esse livro não existe.")
    else:
        meus_livros[id]=livro.model_dump() 
        return {"message": "Informações atualizadas com sucesso"}

@app.delete("/deletar/{id}")
def delete_livro(id: int, credentials: HTTPBasicCredentials = Depends(security)):
    if id not in meus_livros:
         raise HTTPException(status_code=404, detail="Esse livro não existe.")
    else:
        del meus_livros[id]
        return {"message": "Livro deletado com sucesso"}