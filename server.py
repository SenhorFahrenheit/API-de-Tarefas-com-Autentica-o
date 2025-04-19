import socket

# Definição da classe Server
class Server:
    def __init__(self, host='localhost', port=8080):
        # Inicialização do servidor com host e porta definidos
        self.host = host
        self.port = port
        self.routes = {
            'GET': {},
            'POST': {}
        }
    
    def add_route(self, method, path, handler):
        # Método para adicionar uma rota de requisição ao servidor
        print("Rota adicionada!")
        self.routes[method.upper()][path] = handler  # Associa um handler a uma rota
        print(self.routes)
    
    def start(self):
        # Método para iniciar o servidor e começar a ouvir requisições
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))  # Associa o servidor ao host e porta
        sock.listen(5)  # Permite até 5 conexões simultâneas

        print(f"[INICIANDO API] Servidor rodando em {self.host}: {self.port}")

        while True:
            # Aguarda por requisições de clientes
            client, address = sock.accept()
            request = client.recv(5000).decode()  # Lê a requisição do cliente

            if request:
                print("Requisição Recebida")
                response = self.handle_request(request)  # Processa a requisição
                client.sendall(response.encode('utf-8'))  # Envia a resposta para o cliente
                client.close()
    
    def handle_request(self, request):
        # Método que lida com a requisição recebida
        try:
            lines = request.split('\r\n')  # Divide a requisição em linhas
            request_line = lines[0]
            parts = request_line.split()  # Separa a linha de requisição em partes

            if len(parts) >= 2:
                method = parts[0]  # Método HTTP (GET, POST, etc.)
                path = parts[1]  # Caminho da URL
            else:
                return self.http_response(400, "Bad Request", "Linha de requisição inválida")

            headers = {}
            body = ""

            # Separa os headers e o corpo da requisição
            empty_line_index = lines.index('')
            header_lines = lines[1:empty_line_index]
            body_lines = lines[empty_line_index + 1:]
            body = "\n".join(body_lines)

            # Verifica se existe um handler para o método e caminho solicitados
            handler = self.routes.get(method.upper(), {}).get(path)
            print(handler)
            if handler:
                return handler(headers, body)  # Chama o handler correspondente
            else:
                return self.http_response(404, "Not Found", "Rota não encontrada")

        except Exception as e:
            # Caso ocorra algum erro, retorna uma resposta de erro
            return self.http_response(500, "Erro Interno", f"Erro: {e}")
        
    def http_response(self, status_code, status_text, content, content_type='text/html'):
        # Método para gerar uma resposta HTTP formatada
        return (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(content.encode('utf-8'))}\r\n"
        f"Connection: close\r\n\r\n"
        f"{content}"
    )

# ## Rotas da API
# Definem os endpoints de autenticação e gerenciamento de tarefas.

# Cria o servidor e registra as rotas
servidor = Server()

# Importa módulos necessários para as funções de autenticação e tarefas
from server import servidor
from database.model import user_table, tasks_table, connection
from sqlalchemy import select, insert
from utils.functions import gerar_hash, verificar_senha
import json

# Função para realizar o login (POST /sign_in)
def rota_sign_in(headers, body):
    try:
        data = json.loads(body)  # Converte o corpo da requisição para dicionário
        username = data.get("username")
        password = data.get("password")

        # Realiza consulta no banco de dados para verificar o usuário
        user_query = select(user_table).where(user_table.c.username == username)
        result_user = connection.execute(user_query).fetchone()
        if result_user:
            senha_hash = result_user[2]  # Recupera o hash da senha do usuário
            resultado = verificar_senha(password, senha_hash)  # Verifica se a senha está correta
            if resultado:
                response_data = {
                    "message": "Login bem-sucedido",
                    "token": "abc.def.ghi"  # Simulação de um token JWT
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

# Função para realizar o cadastro de usuário (POST /sign_up)
def rota_sign_up(headers, body):
    try:
        data = json.loads(body)  # Converte o corpo da requisição para dicionário
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return servidor.http_response(400, "Bad Request", "Usuário e senha são obrigatórios")

        query = select(user_table).where(user_table.c.username == username)
        result = connection.execute(query).fetchone()
        
        if result:
            return servidor.http_response(409, "Conflict", "Usuário já existe")
        
        password = gerar_hash(password)  # Gera o hash da senha

        insert_query = insert(user_table).values(username=username, password_hash=password)
        connection.execute(insert_query)
        connection.commit()

        return servidor.http_response(201, "Created", "Usuário cadastrado com sucesso")

    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")

# Função para obter tarefas (GET /get_tasks)
def get_tasks(headers, body):
    try:
        data = json.loads(body)  # Converte o corpo da requisição para dicionário

        user_id = data.get("user_id")  # Obtém o ID do usuário
        if not user_id:
            return servidor.http_response(400, "Bad Request", "O id do usuário não pode ser vazio")
        
        query = select(tasks_table).where(tasks_table.c.user_id == user_id)
        resultado = connection.execute(query).fetchall()

        # Transforma o resultado em uma lista de dicionários
        tarefas = [
            {
                "id": row.id,
                "titulo": row.title,
                "descricao": row.description,
                "status": row.done,
                "user_id": row.user_id
            }
            for row in resultado
        ]

        return servidor.http_response(200, "OK", json.dumps(tarefas))
    except json.JSONDecodeError:
        return servidor.http_response(400, "Bad Request", "JSON inválido")
    except Exception as e:
        return servidor.http_response(500, "Internal Server Error", f"Erro no servidor: {str(e)}")

# Função para adicionar tarefas (POST /add_tasks)
def add_tasks(headers, body):
    try:
        data = json.loads(body)  # Converte o corpo da requisição para dicionário
        
        # Extrai valores necessários
        title = data.get("title")
        description = data.get("description", "")
        done = data.get("done", False)
        user_id = data.get("user_id")
        
        if not title:
            return servidor.http_response(400, "Bad Request", "O título da tarefa não pode ser vazio.")
        
        # Prepara os dados para inserção no banco
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

# Registro das rotas no servidor
servidor.add_route("POST", "/add_tasks", add_tasks)
servidor.add_route("POST", "/sign_in", rota_sign_in)
servidor.add_route("POST", "/sign_up", rota_sign_up)
servidor.add_route("GET", "/get_tasks", get_tasks)

# Inicia o servidor
if __name__ == "__main__":
    servidor.start()
