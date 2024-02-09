from fastapi import FastAPI, HTTPException
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis_db = get_redis_connection(
    host="redis-17813.c135.eu-central-1-1.ec2.cloud.redislabs.com",
    port=17813,
    password="jcFnyE7aaRCdMHp0UsBSGc4q4ladeht9",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis_db


@app.get("/products")
def ProductList():
    return [ProductFormat(pk) for pk in Product.all_pks()]

def ProductFormat(pk: str):
    product = Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post("/create_product")
def CreateProduct(product: Product):
    return product.save()

@app.get("/products/{pk}")
def ProductDetail(pk: str):
    return Product.get(pk)

@app.delete("/products/{pk}/delete")
def DeleteProduct(pk:str):
    return Product.delete(pk)


@app.put("/products/{pk}/update")
def UpdateProduct(pk: str):
    return Product.update(pk)
    

