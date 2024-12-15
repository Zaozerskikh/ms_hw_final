from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from database import SessionLocal, engine, Base
from models import TodoItem as TodoItemModel
from pydantic import BaseModel

app = FastAPI(
    title="Семинар наставника hw_final todo_list",
    description="Семинар наставника hw_final todo_list",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)


class TodoItemBase(BaseModel):
    title: str
    description: Union[str, None] = None
    completed: bool = False


class TodoItemCreate(TodoItemBase):
    pass


class TodoItemResponse(TodoItemBase):
    id: int

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/items", response_model=TodoItemResponse)
def create_item(item: TodoItemCreate, db: Session = Depends(get_db)):
    db_item = TodoItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items", response_model=List[TodoItemResponse])
def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TodoItemModel).offset(skip).limit(limit).all()


@app.get("/items/{item_id}", response_model=TodoItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.put("/items/{item_id}", response_model=TodoItemResponse)
def update_item(item_id: int, item: TodoItemBase, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", response_model=TodoItemResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return db_item
