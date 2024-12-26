from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from pydantic import BaseModel
from enum import Enum as PyEnum
from database import get_db
class PostUser(BaseModel):
    email:str
    name:str
class PostOrder(BaseModel):
    id:int
    email:str
    food_name:str
    quantity:int

app = FastAPI()
#user part

@app.post("/create")
async def create_user(payload:PostUser, db:Session=Depends(get_db)):
    query = text(f"insert into users (email, name) values (:email, :name)")
    db.execute(query, dict(payload))
    db.commit()
    return {"message": "User created successfully"}
@app.delete("/delete/{email}")
async def delete_user(email: str, db: Session = Depends(get_db)):
    query = text("delete from users where email = :email")
    result = db.execute(query, {"email": email})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
@app.put("/update/{email}")
async def update_user(email: str, payload: PostUser, db: Session = Depends(get_db)):
    query = text("update users set email = :email, name = :name where email = :old_email")
    result = db.execute(query, {"email": payload.email, "name": payload.name, "old_email": email})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}


@app.get("/get/{email}")
async def get_user(email: str, db: Session = Depends(get_db)):
    query = text("SELECT email, name FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": result[0], "name": result[1]}


#Food
class FoodItem(BaseModel):
    item_name: str
    price: int

# Create food item
@app.post("/create_food")
async def create_food(food: FoodItem, db: Session = Depends(get_db)):
    query = text("INSERT INTO fooditems (item_name, price) VALUES (:item_name, :price)")
    db.execute(query, {"item_name": food.item_name, "price": food.price})
    db.commit()
    return {"message": "Food item created successfully"}



@app.delete("/delete_food/{food_id}")
async def delete_food(food_id: int, db: Session = Depends(get_db)):
    query = text("DELETE FROM fooditems WHERE id = :food_id")
    result = db.execute(query, {"food_id": food_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Food item not found")
    return {"message": "Food item deleted successfully"}


@app.put("/update_food/{food_id}")
async def update_food(food_id: int, food: FoodItem, db: Session = Depends(get_db)):
    query = text("UPDATE fooditems SET item_name = :item_name, price = :price WHERE id = :food_id")
    result = db.execute(query, {"item_name": food.item_name, "price": food.price, "food_id": food_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Food item not found")
    return {"message": "Food item updated successfully"}



@app.get("/get_food/{food_id}")
async def get_food(food_id: int, db: Session = Depends(get_db)):
    query = text("SELECT * FROM fooditems WHERE id = :food_id")
    result = db.execute(query, {"food_id": food_id}).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Food item not found")
    return {"id": result[0], "item_name": result[1], "price": result[2]}

#order

@app.post("/order")
async def create_order(payload:PostOrder, db:Session=Depends(get_db)):
    temp = dict(payload)
    query_find_item = text("select * from fooditems where item_name = :item_name")
    buffer1 = db.execute(query_find_item, {"item_name": temp['food_name']})
    result1 = buffer1.fetchone()
    order = {
        "id": temp['id'], 
        "email": temp['email'],
        "item_id": result1[0],
        "food_name": temp['food_name'],
        "quantity": temp['quantity'],
        "total_price": temp['quantity']*result1[2]
    }
    query_insert_order = text(f"insert into orders (id, email, item_id, food_name, quantity, total_price) values (:id, :email, :item_id, :food_name,:quantity, :total_price)")    
    db.execute(query_insert_order, order)
    db.commit()
    query_status_table = text(f"insert into orderstatus (order_id, status, total) values (:order_id, :status, :total)")
    db.execute(query_status_table, {"order_id":order['id'], "status": "pending", "total": order['total_price']})
    db.commit()
    return {"msg":"order submited!"}


#orderStatus

class OrderStatusEnum(PyEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"

class UpdateOrderStatus(BaseModel):
    status: OrderStatusEnum


@app.put("/admin/update_order_status/{order_id}")
async def update_order_status(order_id: int, payload: UpdateOrderStatus, db: Session = Depends(get_db)):
    query = text("SELECT * FROM orders WHERE id = :order_id")
    result = db.execute(query, {"order_id": order_id}).fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Order not found")
    update_query = text("""
        UPDATE orderstatus 
        SET status = :status 
        WHERE order_id = :order_id
    """)
    db.execute(update_query, {"status": payload.status, "order_id": order_id})
    db.commit()
    return {"message": f"Order {order_id} status updated to {payload.status.value}"}





