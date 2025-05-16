from pymongo import MongoClient
from config import MONGO_URI

try:
    client = MongoClient(MONGO_URI)
    db = client['LimonPersa_Proyect']
    usuarios = db['usuarios']
    print("Conexión exitosa a MongoDB Atlas")
    for user in usuarios.find():
        print(user)
except Exception as e:
    print(f"Error al conectar a MongoDB Atlas: {e}")