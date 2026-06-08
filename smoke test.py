from pymongo import MongoClient

client = MongoClient("mongodb://itc6050:itc6050@localhost:27017/?authSource=admin")
print(client.server_info()["version"])