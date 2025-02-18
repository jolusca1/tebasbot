import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_TOKEN"))
database = client['tebasBot']
users = database['users']

async def newUser(user):
    filter_query = {"discord_id": user.id}
    
    if users.count_documents(filter_query) == 0:
        userObject = {
            "discord_id": user.id,
            "points": 10
        }
        users.insert_one(userObject)
        return userObject
    return False
    
# Verificar pontos do usuário
async def check_points(user):
    await newUser(user)  # Garantir que o usuário existe
    
    filter_query = {"discord_id": user.id}
    result = users.find_one(filter_query)
    
    return result["points"] if result else 0

# Alterar pontos do usuário
async def changePoints(user, quantity):
    await newUser(user)  # Garantir que o usuário existe
    
    actuallyPoints = await check_points(user)  # Buscar os pontos atuais
    
    filter_query = {"discord_id": user.id}  # Nome corrigido
    update_query = {
        "$set": {"points": actuallyPoints + quantity}  # Nome corrigido para "points"
    }
    
    users.update_one(filter_query, update_query)      