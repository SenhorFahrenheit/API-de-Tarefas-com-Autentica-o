# PEÇA ESSENCIAL DO BACKEND -> CONEXÃO COM O BANCO DE DADOS
import sqlalchemy as db
from sqlalchemy import ForeignKey, Table, Column, Boolean, Integer, String, MetaData
engine = db.create_engine("sqlite:///API-Tarefas.db")
connection = engine.connect()
metadata_obj = MetaData()

user_table = Table(
    "user_table",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(40), unique=True),
    Column("password_hash", String(128), nullable=False)

)
tasks_table = Table(
    "tasks_table",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(40), nullable=False),
    Column("description", String(128), nullable=False),
    Column("done", Boolean, nullable=False),
    Column("user_id", ForeignKey("user_table.id"), nullable=False)

)

metadata_obj.create_all(engine)

