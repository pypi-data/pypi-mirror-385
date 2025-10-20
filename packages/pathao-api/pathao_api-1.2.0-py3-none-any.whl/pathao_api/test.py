from .core import PathaoAPI

client = PathaoAPI()

#print(client.get_delivery_charge(3,535))
#print(client.get_stores())
print(client.get_city_list())
