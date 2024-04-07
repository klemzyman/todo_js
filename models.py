from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, unique=True, nullable=False)
    email = mapped_column(String, unique=True)
    secret_number = mapped_column(Integer)
    passwd = mapped_column(String(40))
    session_token = mapped_column(String(40))


class Todo(db.Model):
    id = mapped_column(Integer, primary_key=True)
    task = mapped_column(String)
    priority = mapped_column(String)
    due_date = mapped_column(Date)
    completed = mapped_column(Boolean)
