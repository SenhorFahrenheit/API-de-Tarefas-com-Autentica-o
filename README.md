# 🧠 Projeto: Servidor de Tarefas com Autenticação

Este projeto é um servidor básico HTTP feito com **Python puro (sockets)** e **SQLAlchemy**, que permite aos usuários **realizar login, cadastrar-se, criar tarefas e visualizar suas tarefas**, tudo persistido em um **banco SQLite**.

---

## 🔧 Funcionalidades

- **Autenticação de Usuário**:
  - Rota de login que gera um token de autenticação (simulado).
  - Cadastro de novos usuários com validação e hash de senha.

- **Gerenciamento de Tarefas**:
  - Criação de novas tarefas vinculadas ao usuário.
  - Listagem das tarefas de um usuário autenticado.

- **Validação Manual**:
  - Dados recebidos no corpo da requisição são processados com `json.loads()`.

- **Servidor Simples via Socket**:
  - Manipulação de requisições HTTP manualmente.
  - Definição de rotas com métodos `GET` e `POST`.

---

## 📁 Estrutura do Projeto

```
.
├── server.py               # Lógica principal do servidor HTTP
├── database/
│   └── model.py            # Definição das tabelas (usuários e tarefas)
├── utils/
│   └── functions.py        # Funções auxiliares (hash, verificação de senha, etc.)
├── README.md               # Documentação do projeto
└── requirements.txt        # Dependências do projeto (ex: SQLAlchemy)
```

---

## 📌 Endpoints Disponíveis

| Método | Rota         | Descrição                              |
|--------|--------------|----------------------------------------|
| POST   | /sign_up     | Cadastro de usuário                    |
| POST   | /sign_in     | Login do usuário (retorna token fake) |
| POST   | /add_tasks   | Adiciona nova tarefa                   |
| GET    | /get_tasks   | Retorna todas as tarefas do usuário    |

> **Nota**: As requisições são feitas diretamente com `JSON` no corpo. Algumas rotas exigem o `user_id` como parte do corpo para funcionar corretamente.

---

## 🧲 Exemplos de Requisição

### ✅ Login (`/sign_in`)

```http
POST /sign_in
Content-Type: application/json

{
  "username": "usuario1",
  "password": "123456"
}
```

### 📝 Criar Tarefa (`/add_tasks`)

```http
POST /add_tasks
Content-Type: application/json

{
  "title": "Estudar Python",
  "description": "Avançar nos estudos de back-end",
  "done": false,
  "user_id": 1
}
```

### 📋 Listar Tarefas (`/get_tasks`)

```http
GET /get_tasks
Content-Type: application/json

{
  "user_id": 1
}
```

---

## 🛠️ Como Rodar o Projeto

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repo.git
   cd nome-do-repo
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Certifique-se de que o banco está configurado corretamente (em `model.py`).

4. Inicie o servidor:
   ```bash
   python server.py
   ```

---

## 🧠 Tecnologias Usadas

- Python (socket)
- SQLAlchemy (ORM)
- SQLite
- JSON

---

## 📌 Observações

- O token retornado no login ainda é fictício.
- A autenticação por middleware está implementada de forma conceitual.
- O projeto é ideal para fins de **aprendizado** e demonstra como montar uma API funcional sem frameworks prontos como Flask ou FastAPI.

