from sqlalchemy import Float,Column, String, Text, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, inspect

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


Base = declarative_base()

DB_URL = f"mysql+pymysql://root:@127.0.0.1:3306/foodiehub"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class FoodItems(Base):
    __tablename__ = "fooditems"
    id = Column(Integer, primary_key=True)
    item_name = Column(String(250))
    price = Column(Float)

class Users(Base):
    __tablename__ = "users"

    email = Column(String(250), primary_key=True)
    name = Column(String(250))

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    email = Column(String(250), ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'))
    item_id = Column(Integer, ForeignKey('fooditems.id', ondelete='CASCADE', onupdate='CASCADE'))

    food_name = Column(String(250))
    quantity = Column(Integer)
    total_price = Column(Float)
    

class OrderStatus(Base):
    __tablename__ = "orderstatus"

    order_id =  Column(Integer, ForeignKey('orders.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    status = Column(String(250))
    total = Column(Float)



Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
