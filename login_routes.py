# - **POST /login**: Autenticação de usuários com envio de nome de usuário e senha. Retorna um token ou cookie.
from server import servidor
from database.model import user_table, connection
from sqlalchemy import select, insert
from utils.functions import gerar_hash, verificar_senha

import json

def rota_sign_in(headers, body):
    try:
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")

        # Realiza a consulta no banco de dados
        user_query = select(user_table).where(user_table.c.username == username)
        result_user = connection.execute(user_query).fetchone()

        if result_user:
            senha_hash = result_user['password_hash']  # Acessando com a chave
            resultado = verificar_senha(password, senha_hash)

            if resultado:
                response_data = {
                    "message": "Login bem-sucedido",
                    "token": "abc.def.ghi"  # Simulação de token
                }
                return servidor.http_response(200, "OK", json.dumps(response_data), content_type="application/json")
            else:
                return servidor.http_response(401, "Unauthorized", "Usuário ou senha incorretos.")
        else:
            return servidor.http_response(401, "Unauthorized", "Usuário não encontrado.")

    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")
    except Exception as e:
        return servidor.http_response(500, "Internal Server Error", f"Erro no servidor: {str(e)}")


def rota_sign_up(headers, body):
    try:
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return servidor.http_response(400, "Bad Request", "Usuário e senha são obrigatórios")

        query = select(user_table).where(user_table.c.username == username)
        result = connection.execute(query).fetchone()

        if result:
            return servidor.http_response(409, "Conflict", "Usuário já existe")
        
        password = gerar_hash(password)

        insert_query = insert(user_table).values(username=username, password_hash=password)
        result_insert = connection.execute(insert_query).fetchone()

        return servidor.http_response(201, "Created", "Usuário cadastrado com sucesso")

    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")

      
servidor.add_route("POST", "/sign_in", rota_sign_in)
servidor.add_route("POST", "/sign_up", rota_sign_up)
