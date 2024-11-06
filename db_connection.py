from pymongo import MongoClient
from urllib.parse import quote_plus

username = quote_plus("adilharoon304")
password = quote_plus("Adil@304")

uri = f'mongodb+srv://{username}:{password}@cluster0.xym4o.mongodb.net/'
client = MongoClient(uri)
db = client['cluster0']