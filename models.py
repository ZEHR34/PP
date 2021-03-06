from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, ForeignKey, VARCHAR, DateTime, Boolean
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.types import Boolean
from sqlalchemy.orm import relationship
from connection_string import connection_string
from marshmallow import Schema, fields, post_load

engine = create_engine(connection_string)
engine.connect()

SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)


Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    id = Column(Integer(), primary_key=True)
    username = Column(String(100), nullable=False)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    password = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=True)

    wallets = relationship("Wallet", backref="owner")   



class Wallet(Base):
    __tablename__ = "Wallet"

    id = Column(Integer(), primary_key=True)
    privacy = Column(Boolean(), default=False)
    owner_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    value  = Column(Integer(), nullable=False)



class Transaction(Base):
    __tablename__ = "Transaction"

    id = Column(Integer(), primary_key=True)
    value  = Column(Integer(), nullable=False)
    sender_id = Column(Integer(), ForeignKey(Wallet.id), nullable=False)
    recipient_id = Column(Integer(), ForeignKey(Wallet.id), nullable=False)

    sender = relationship("Wallet", foreign_keys="Transaction.sender_id", backref="sended")
    recipient = relationship("Wallet", foreign_keys="Transaction.recipient_id", backref="recipiented")
