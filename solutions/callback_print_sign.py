def callback(old_value, value, **kwargs):
    if old_value < value:
        print("+")
    else:
        print("-")
        

token = x.subscribe(callback)
# To turn off:
# x.unsubscribe(token)