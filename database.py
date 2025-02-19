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
    await newUser(user)

    filter_query = {"discord_id": user.id}
    user_data = users.find_one(filter_query)

    if not user_data:
        return 0

    # Pontos base do usuário
    base_points = user_data.get("points", 0)

    game_points = sum(g["score"] for g in user_data.get("games_completed", []))

    return base_points + game_points

# Alterar pontos do usuário
async def changePoints(user, quantity):
    await newUser(user)  # Garantir que o usuário existe
    
    actuallyPoints = await check_points(user)  # Buscar os pontos atuais
    
    filter_query = {"discord_id": user.id}  # Nome corrigido
    update_query = {
        "$set": {"points": actuallyPoints + quantity}  # Nome corrigido para "points"
    }
    
    users.update_one(filter_query, update_query)
    
async def getRanking(limit=10):
    ranking = users.find().sort("points", -1).limit(limit)  # Ordena por pontos (maior para menor)
    
    ranking_list = []
    for i, user in enumerate(ranking, start=1):
        ranking_list.append(f"{i}. <@{user['discord_id']}> - {user['points']} pontos")

    return ranking_list

def getNextGameID():
    """Obtém o próximo ID disponível para um jogo."""
    counter = database["counters"]
    result = counter.find_one_and_update(
        {"_id": "game_id"},
        {"$inc": {"seq": 1}},
        upsert=True,  # Se não existir, cria
        return_document=pymongo.ReturnDocument.AFTER
    )
    return result["seq"]

# Adicionar um jogo ao banco com ID incremental
async def addGame(name, score):
    if games.find_one({"name": name}):  # Evita duplicatas pelo nome
        return False, "Esse jogo já está cadastrado!"

    game_data = {
        "game_id": getNextGameID(),  # Gera ID incremental
        "name": name,
        "score": score
    }
    games.insert_one(game_data)
    return True, f"Jogo **{name}** adicionado com {score} pontos! ID: {game_data['game_id']}"
