from fastapi import FastAPI, HTTPException
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

#This should be a different database, but it isn't because i would need to pay for second one on Redis.
redis_db = get_redis_connection(
    host="redis-17813.c135.eu-central-1-1.ec2.cloud.redislabs.com",
    port=17813,
    password="jcFnyE7aaRCdMHp0UsBSGc4q4ladeht9",
    decode_responses=True
)



class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #pending, completed, refunded


    class Meta:
        database = redis_db

@app.get("/orders/{pk}")
def OrderDetail(pk: str):
    return Order.get(pk)

@app.post("/orders")
async def CreateOrder(request: Request, background_tasks: BackgroundTasks): #id, quantity
    body = await request.json()
    req = requests.get("http://localhost:8000/products/%s" % body['id'])
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total= 1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(2)
    order.status = 'completed'
    order.save()
    redis_db.xadd('order_completed', order.dict(), '*')