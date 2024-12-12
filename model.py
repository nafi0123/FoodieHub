from sqlalchemy import Boolean, Column, Integer, String, Text, DECIMAL, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "Users"
    User_ID = Column(Integer, primary_key=True, autoincrement=True)
    User_name = Column(String(50), nullable=False, unique=True)  # Username must be unique
    Password = Column(String(60), nullable=False)  
    Email = Column(String(50), nullable=False, unique=True)  # Email must be unique
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class FoodItem(Base):
    __tablename__ = "Food_Items"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    food_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    # Add a constraint to ensure price is positive
    __table_args__ = (CheckConstraint('price > 0', name='check_price_positive'),)
    orders = relationship("Order", back_populates="item", cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = "Orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    item_Id = Column(Integer, ForeignKey("Food_Items.ID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.User_ID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    food_name = Column(String(100), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    # Add constraints to ensure total_price is positive and quantity is at least 1
    __table_args__ = (
        CheckConstraint('quantity >= 1', name='check_quantity_positive'),
        CheckConstraint('total_price > 0', name='check_total_price_positive'),
    )
    user = relationship("User", back_populates="orders")
    item = relationship("FoodItem", back_populates="orders")
    status = relationship("OrderStatus", back_populates="order", uselist=False)

class OrderStatus(Base):
    __tablename__ = "Order_Status"
    status_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("Orders.order_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    # Add a constraint to ensure total_price is positive
    __table_args__ = (CheckConstraint('total_price > 0', name='check_status_total_price_positive'),)
    order = relationship("Order", back_populates="status")
