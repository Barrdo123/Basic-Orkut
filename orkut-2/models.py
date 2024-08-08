from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "Usuario"

    usuario = Column(String(20), primary_key=True)
    nome = Column(String(64))
    sobrenome = Column(String(64))
    senha = Column(String(102))
    criado_em = Column(DateTime, default=datetime.now)


class Post(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    de = Column(ForeignKey("Usuario.usuario"))
    para = Column(ForeignKey("Usuario.usuario"))
    conteudo = Column(String)
    criado_em = Column(DateTime, default=datetime.now)