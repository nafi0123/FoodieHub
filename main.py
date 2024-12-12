from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import model
from model import User,FoodItem,Order,OrderStatus
from typing import List
from database import engine, sessonlocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
model.Base.metadata.create_all(bind=engine)
app = FastAPI()
class UserCreate(BaseModel):
    User_name: str
    password: str
    Email: str
class UserOut(BaseModel):
    User_ID: int
    User_name: str
    Email: str
class UserUpdate(BaseModel):
    User_name: str
    Password: str
    Email: str
def get_db():
    db = sessonlocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.User_name == user.User_name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(
        User_name=user.User_name,
        Password=hashed_password,
        Email=user.Email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}",response_model=UserOut)
def get_user(user_id:int, db:Session = Depends(get_db)):
    user=db.query(User).filter(User.User_ID==user_id).first()

    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")
    return user

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.User_ID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    db_user.User_name = user.User_name
    db_user.Password = hash_password(user.Password)
    db_user.Email = user.Email
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.User_ID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

class Login(BaseModel):
    User_name: str
    Password: str
@app.post("/login")
def login(login_data: Login, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.User_name == login_data.User_name).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")    
    print(f"Database Password: {db_user.Password}") 
    if not verify_password(login_data.Password, db_user.Password):
        raise HTTPException(status_code=401, detail="Invalid credentials")    
    return {"message": "Login successful"}



class FoodItemCreate(BaseModel):
    food_name: str
    category: str
    description: str
    price: float

class FoodItemOut(BaseModel):
    ID: int
    food_name: str
    category: str
    description: str
    price: float

@app.post("/food-items", response_model=FoodItemOut)
async def add_food_item(food_item: FoodItemCreate, db: Session = Depends(get_db)):
    new_food_item = FoodItem(
        food_name=food_item.food_name,
        category=food_item.category,
        description=food_item.description,
        price=food_item.price
    )
    db.add(new_food_item)
    db.commit()
    db.refresh(new_food_item)
    return new_food_item



@app.get("/food-items", response_model=List[FoodItemOut])
async def get_food_items(db: Session = Depends(get_db)):
    return db.query(FoodItem).all()



@app.get("/food-items/{food_item_id}", response_model=FoodItemOut)
async def get_food_item(food_item_id: int, db: Session = Depends(get_db)):
    food_item = db.query(FoodItem).filter(FoodItem.ID == food_item_id).first()
    if food_item is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    return food_item


@app.put("/food-items/{food_item_id}", response_model=FoodItemOut)
async def update_food_item(food_item_id: int, food_item: FoodItemCreate, db: Session = Depends(get_db)):
    db_food_item = db.query(FoodItem).filter(FoodItem.ID == food_item_id).first()
    if db_food_item is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    db_food_item.food_name = food_item.food_name
    db_food_item.category = food_item.category
    db_food_item.description = food_item.description
    db_food_item.price = food_item.price
    db.commit()
    db.refresh(db_food_item)
    return db_food_item

@app.delete("/food-items/{food_item_id}", status_code=204)
async def delete_food_item(food_item_id: int, db: Session = Depends(get_db)):
    db_food_item = db.query(FoodItem).filter(FoodItem.ID == food_item_id).first()
    if db_food_item is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    db.delete(db_food_item)
    db.commit()
    return {"message": "Food item deleted successfully"}




class OrderCreate(BaseModel):
    item_Id: int
    user_id: int
    quantity: int
    food_name: str
    total_price: float

class OrderOut(BaseModel):
    order_id: int
    item_Id: int
    user_id: int
    quantity: int
    food_name: str
    total_price: float

@app.post("/orders", response_model=OrderOut)
async def add_order(order: OrderCreate, db: Session = Depends(get_db)):
    food_item = db.query(FoodItem).filter(FoodItem.ID == order.item_Id).first()
    
    if food_item is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    

    total_price = food_item.price * order.quantity

    new_order = Order(
        item_Id=order.item_Id,
        user_id=order.user_id,
        quantity=order.quantity,
        food_name=food_item.food_name,
        total_price=total_price
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order



@app.get("/orders", response_model=List[OrderOut])
async def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    for order in orders:
        food_item = db.query(FoodItem).filter(FoodItem.ID == order.item_Id).first()
        if food_item:
            order.total_price = food_item.price * order.quantity    
    return orders

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    food_item = db.query(FoodItem).filter(FoodItem.ID == order.item_Id).first()
    if food_item:
        order.total_price = food_item.price * order.quantity
    return order




class OrderStatusCreate(BaseModel):
    order_id: int
    status: str
    total_price: float

class OrderStatusOut(BaseModel):
    status_id: int
    order_id: int
    status: str
    total_price: float

@app.post("/order-status", response_model=OrderStatusOut)
async def add_order_status(order_status: OrderStatusCreate, db: Session = Depends(get_db)):
    new_order_status = OrderStatus(
        order_id=order_status.order_id,
        status=order_status.status,
        total_price=order_status.total_price
    )
    db.add(new_order_status)
    db.commit()
    db.refresh(new_order_status)
    return new_order_status

@app.get("/order-status/{status_id}", response_model=OrderStatusOut)
async def get_order_status(status_id: int, db: Session = Depends(get_db)):
    order_status = db.query(OrderStatus).filter(OrderStatus.status_id == status_id).first()
    if order_status is None:
        raise HTTPException(status_code=404, detail="Order status not found")
    return order_status



