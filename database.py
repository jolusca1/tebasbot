import pymongo
from dotenv import load_dotenv
import os
import re
import requests
from google import genai

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_TOKEN"))
database = client['tebasBot']
users = database['users']
games = database['games']

# constantes da api da hugging
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

async def newUser(user):
    filter_query = {"discord_id": user.id}
    
    if users.count_documents(filter_query) == 0:
        userObject = {
            "discord_id": user.id,
            "points": 0
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

    # game_points = sum(g["score"] for g in user_data.get("games_completed", []))

    return base_points

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
    
async def getRankingJogosZerados(limit=10):
        
    pipeline = [
        {"$unwind": "$games_completed"},
        {"$group": {"_id": "$games_completed.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    ranking = list(users.aggregate(pipeline))

    return [(item["_id"], item["count"]) for item in ranking]


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
async def add_game(game_name, score):
    """Adiciona um jogo ao banco de dados sem permitir duplicatas (case insensitive)."""
    
    # Procura um jogo que tenha o mesmo nome, ignorando maiúsculas e minúsculas
    existing_game = games.find_one({"name": {"$regex": f"^{re.escape(game_name)}$", "$options": "i"}})

    if existing_game:
        return f"⚠️ O jogo **{existing_game['name']}** já está cadastrado com {existing_game['score']} pontos."

    # Gera um game_id incremental
    last_game = games.find_one(sort=[("game_id", -1)])
    new_game_id = (last_game["game_id"] + 1) if last_game else 1

    # Insere o jogo no banco
    game_data = {"game_id": new_game_id, "name": game_name, "score": score}
    games.insert_one(game_data)

    return f"✅ Jogo **{game_name}** adicionado com sucesso! (Pontuação: {score})"

async def get_completed_games(user):
    """Retorna a lista de jogos zerados por um usuário e a soma total dos pontos."""
    
    user_data = users.find_one({"discord_id": user.id})
    
    if not user_data or "games_completed" not in user_data or not user_data["games_completed"]:
        return [], 0  # Retorna lista vazia e pontuação 0 se não houver jogos

    games = user_data["games_completed"]
    total_score = sum(game["score"] for game in games)

    return games, total_score

async def get_all_games():    
    
    games_cursor = games.find().sort("name", pymongo.ASCENDING)
    print(games_cursor)
    
    game_list = list(games_cursor)
    
    return game_list

async def get_games_by_name(game_name):
    games_cursor = games.find(
        {"name": {"$regex": re.escape(game_name), "$options": "i"}}
    ).sort("score", -1)

    return list(games_cursor)

async def avaliar_dificuldade_jogo(game_name):
    
    prompt = f"""
    Lembre-se de que esses exemplos são apenas referência. Ao avaliar um jogo individual, responda de forma objetiva em até 10 frases, dando uma nota de 1 a 10 e uma justificativa breve
    
    Para classificar a dificuldade de zerar jogos, considerando fatores como duração, precisão de inputs, quantidade/força de inimigos, mecânicas de combate e de sobrevivência.
    - Fácil: 1-2 (ex.: Minecraft, Pokémon)
    - Normal: 3-5 (ex.: Resident Evil, Hollow Knight)
    - Difícil: 6-8 (ex.: Cuphead, Celeste)
    - Muito Difícil: 9-10 (ex.: Soulslikes, Bloodborne)

    Lembre-se de que esses exemplos são apenas referência. Ao avaliar um jogo individual, responda de forma objetiva em até 10 frases, dando uma nota de 1 a 10 e uma justificativa breve (sem bullet points) seguindo este formato:
    Nota: X/10  
    Justificativa: [resposta em até 10 frases].

    Agora, responda para '{game_name}' seguindo esse formato.

    """

    client = genai.Client(api_key=os.getenv('GEMINI_TOKEN'))
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    if response:
        resposta = response.text
        
        import re
        match = re.search(r'Nota: (\d{1,2})/10', resposta)
        nota = int(match.group(1)) if match and 1 <= int(match.group(1)) <= 10 else None
        
        if nota is None:
            print("⚠️ Erro: A IA não retornou a nota corretamente!")
            print("Resposta recebida:", resposta)

        return nota, resposta

    return None, f"Erro ao acessar API: {response.text}"
