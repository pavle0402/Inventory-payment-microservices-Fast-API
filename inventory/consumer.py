from main import redis_db, Product
import time

key = 'order_completed'
group = 'inventory-group'

try:
    redis_db.xgroup_create(key, group)
except:
    print("Group already exists.")


while True:
    try:
        results = redis_db.xreadgroup(group, key, {key: '>'}, None)
        
        if results != []:
            for result in results:
                obj = result[1][0][1]
                try:
                    product = Product.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                except:
                    redis_db.xadd('refund_order', obj, '*')

    except Exception as e:
        print(str(e))
    time.sleep(1)