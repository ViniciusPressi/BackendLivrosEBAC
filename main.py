# API DE LIVROS

#POST - adicionar livros (Create)
#GET- buscar dados dos livros (Read)
#PUT - atualizar info dos livros (Update)
# DELETE - Deletar info (Delete)
#CRUD

from fastapi import FastAPI, HTTPException

app = FastAPI()

meus_livros = {}

@app.get("/livros")
def get_livros():
    if not meus_livros:
        return{"message": "Esse livro não existe!"}
    else:
        return{"livros":meus_livros}

# id, nome, autor, ano de lançamento
@app.post("/adicionar")
def post_livros(id: int, nome: str, autor: str, ano: int):
    if id in meus_livros:
        raise HTTPException(status_code=400, detail="Esse livro já existe.")
    else:
        meus_livros[id]={"nome":nome, "autor": autor, "ano": ano}
        return {"message": "Livro criado com sucesso!"}

@app.put("/atualizar/{id}")
def put_livros(id: int, nome: str, autor: str, ano: int):
    meu_livro=meus_livros.get(id)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Esse livro não existe.")
    else:
        if nome:
            meu_livro["nome"]=nome
        if autor:
            meu_livro["autor"]=autor
        if ano:
            meu_livro["ano"]=ano
        return {"message": "Informações atualizadas com sucesso"}

@app.delete("/deletar/{id}")
def delete_livro(id: int):
    if id not in meus_livros:
         raise HTTPException(status_code=404, detail="Esse livro não existe.")
    else:
        del meus_livros[id]
        return {"message": "Livro deletado com sucesso"}