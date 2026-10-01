from fastapi import FastAPI
from app.database import Base, engine
from app.models import Product, Category, StockMovement, User
from app.routes.category import router as category_router
from app.routes.product import router as product_router
from app.routes.stock_movement import router as stock_movement_router
from app.routes.auth import router as auth_router


app = FastAPI()

app.include_router(category_router)
app.include_router(product_router)
app.include_router(stock_movement_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "API de gestion de inventario"}