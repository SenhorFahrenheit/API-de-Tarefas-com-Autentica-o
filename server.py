## Funcionalidades
# - **Login**: Endpoint de login que gera um token ou cookie para autenticação.
# - **Manipulação de Tarefas**: Usuários podem criar e visualizar suas tarefas.
# - **Autenticação**: Implementação de middleware que verifica se o usuário está autenticado antes de permitir acesso às rotas protegidas.
# - **Banco de Dados**: Armazenamento de usuários e tarefas em SQLite.
# - **Validação**: Validação manual de dados utilizando `json.loads()`.


import socket


class Server:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.routes = {
            'GET': {},
            'POST': {}
        }
    def add_route(self, method, path, handler):
        print("Rota adicionada!")
        self.routes[method.upper()][path] =  handler
        print(self.routes)
    
    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)

        print(f"[INICIANDO API] Servidor rodando em {self.host}: {self.port}")

        while True:
            client, adress = sock.accept()
            request = client.recv(5000).decode()

            if request:
                print("Requisição Recebida")
                response = self.handle_request(request)
                client.sendall(response.encode('utf-8'))
                client.close()
    def handle_request(self, request):
        try:
            lines = request.split('\r\n')
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) >= 2:
                method = parts[0]
                path = parts[1]
            else:
                return self.http_response(400, "Bad Request", "Linha de requisição inválida")


            headers = {}
            body = ""

              # Separa headers e body
            empty_line_index = lines.index('')
            header_lines = lines[1:empty_line_index]
            body_lines = lines[empty_line_index + 1:]

            body = "\n".join(body_lines)

            handler = self.routes.get(method.upper(), {}).get(path)
            print(handler)
            if handler:
                return handler(headers, body)
            else:
                return self.http_response(404, "Not Found", "Rota não encontrada")


        except Exception as e:
            return self.http_response(500, "Erro Interno", f"Erro: {e}")
        
    def http_response(self, status_code, status_text, content, content_type='text/html'):
        return (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(content.encode('utf-8'))}\r\n"
        f"Connection: close\r\n\r\n"
        f"{content}"
    )


# ## Rotas da API
# - **POST /login**: Autenticação de usuários com envio de nome de usuário e senha. Retorna um token ou cookie.
# - **GET /tarefas**: Retorna todas as tarefas do usuário autenticado.
# - **POST /tarefas**: Cria uma nova tarefa para o usuário autenticado.



# Cria o servidor e registra as rotas
servidor = Server()
# servidor.add_route("GET", "/", rota_html)               # Adiciona a rota GET /

# - **POST /login**: Autenticação de usuários com envio de nome de usuário e senha. Retorna um token ou cookie.
from server import servidor
from database.model import user_table, tasks_table, connection
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
            senha_hash = result_user[2]  # Acessando com a chave
            print(senha_hash)
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
    print(json.loads(body))
    try:
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")
        print(username)
        print(password)
        if not username or not password:
            return servidor.http_response(400, "Bad Request", "Usuário e senha são obrigatórios")

        query = select(user_table).where(user_table.c.username == username)
        result = connection.execute(query).fetchone()
        
        if result:
            return servidor.http_response(409, "Conflict", "Usuário já existe")
        
        password = gerar_hash(password)

        insert_query = insert(user_table).values(username=username, password_hash=password)
        connection.execute(insert_query)
        connection.commit()

        return servidor.http_response(201, "Created", "Usuário cadastrado com sucesso")

    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")

def get_tasks():
    pass

def add_tasks(headers, body):
    try:
        # Converte o corpo da requisição para um dicionário Python
        data = json.loads(body)
        
        # Extraímos os valores necessários do corpo
        title = data.get("title")
        description = data.get("description", "")
        done = data.get("done", False)
        user_id = data.get("user_id")
        
        # Validação simples: título não pode ser vazio
        if not title:
            return servidor.http_response(400, "Bad Request", "O título da tarefa não pode ser vazio.")
        
        # Prepara o dicionário de tarefa para inserção
        tarefa = {
            "title": title,
            "description": description,
            "done": done,
            "user_id": user_id
        }

        # Insere a tarefa no banco de dados
        insert_tasks = insert(tasks_table).values(
            title=tarefa["title"],
            description=tarefa["description"],
            done=tarefa["done"],
            user_id=tarefa["user_id"]
        )
        connection.execute(insert_tasks)
        connection.commit()

        # Responde com sucesso
        return servidor.http_response(201, "Created", "Tarefa adicionada com sucesso", content_type="application/json")
    
    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")
    except Exception as e:
        return servidor.http_response(500, "Internal Server Error", f"Erro no servidor: {str(e)}")



servidor.add_route("POST", "/add_tasks", add_tasks)
servidor.add_route("POST", "/sign_in", rota_sign_in)
servidor.add_route("POST", "/sign_up", rota_sign_up)



# Inicia o servidor
if __name__ == "__main__":
    servidor.start()
