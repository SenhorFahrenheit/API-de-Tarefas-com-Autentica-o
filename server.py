## Funcionalidades
# - **Login**: Endpoint de login que gera um token ou cookie para autenticação.
# - **Manipulação de Tarefas**: Usuários podem criar e visualizar suas tarefas.
# - **Autenticação**: Implementação de middleware que verifica se o usuário está autenticado antes de permitir acesso às rotas protegidas.
# - **Banco de Dados**: Armazenamento de usuários e tarefas em SQLite.
# - **Validação**: Validação manual de dados utilizando `json.loads()`.

# ## Rotas da API
# - **POST /login**: Autenticação de usuários com envio de nome de usuário e senha. Retorna um token ou cookie.
# - **GET /tarefas**: Retorna todas as tarefas do usuário autenticado.
# - **POST /tarefas**: Cria uma nova tarefa para o usuário autenticado.

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
        self.routes[method.upper()][path] =  handler
    
    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
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
            method, path = request_line.split()

            headers = {}
            body = ""

            index = lines.index('')
            header_lines = lines[1:index]
            body_lines = lines[index:1]

            for line in header_lines:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value

            if method.upper() == 'POST':
                pass

            if method.upper() == "GET":
                pass


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
    