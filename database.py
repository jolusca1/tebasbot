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
async def add_game(game_name, nota, criterios):
    """Adiciona um jogo ao banco de dados sem permitir duplicatas (case insensitive)."""
    
    # Procura um jogo que tenha o mesmo nome, ignorando maiúsculas e minúsculas
    existing_game = await is_game_exist(game_name)

    if existing_game:
        return f"⚠️ O jogo **{existing_game['name']}** já está cadastrado com {existing_game['score']} pontos."

    # Gera um game_id incremental
    last_game = games.find_one(sort=[("game_id", -1)])
    new_game_id = (last_game["game_id"] + 1) if last_game else 1

    # Insere o jogo no banco
    game_data = {
        "game_id": new_game_id, 
        "name": game_name, 
        "score": nota,
        "criterios": criterios
    }
    games.insert_one(game_data)

    return f"✅ Jogo **{game_name}** adicionado com sucesso! (Pontuação: {nota})"

# method para verificar se um jogo existe no banco
async def is_game_exist(game_name):
    game = games.find_one({"name": {"$regex": f"^{re.escape(game_name)}$", "$options": "i"}})
    if not game:
        return False
    return game

async def get_completed_games(user):
    """Retorna a lista de jogos zerados por um usuário e a soma total dos pontos."""
    
    user_data = users.find_one({"discord_id": user.id})
    
    if not user_data or "games_completed" not in user_data or not user_data["games_completed"]:
        return [], 0  # Retorna lista vazia e pontuação 0 se não houver jogos

    games_completed = user_data["games_completed"]
    total_score = sum(game["score"] for game in games_completed)

    return games_completed, total_score

async def get_all_games():    
    
    games_cursor = games.find().sort("name", pymongo.ASCENDING)
    return list(games_cursor)

async def get_games_by_name(game_name, find_one=False):
    
    if find_one:
        games_cursor = games.find_one(
            {"name": {"$regex": re.escape(game_name)}}
        )
        if games_cursor:
            return games_cursor
        return False
        
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

    Lembre-se de que esses exemplos são apenas referência. Ao avaliar um jogo individual, responda seguindo este formato:
    
    Nota: X/10
    
    Critérios para Zerar:
    [Liste 3-5 critérios principais que precisam ser cumpridos para considerar o jogo como zerado]
    
    Justificativa da Nota:
    [Explique em até 5 frases por que essa nota foi atribuída]

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
        # Procura por padrões de nota com ou sem negrito/asteriscos
        nota_patterns = [
            r'Nota:\s*(\d{1,2})/10',  # Padrão normal
            r'Nota:\s*\*\*(\d{1,2})/10\*\*',  # Padrão com negrito markdown
            r'\*\*Nota:\*\*\s*(\d{1,2})/10',  # Padrão com título em negrito
            r'\*\*Nota:\s*(\d{1,2})/10\*\*'   # Padrão com tudo em negrito
        ]
        
        nota = None
        for pattern in nota_patterns:
            match = re.search(pattern, resposta)
            if match:
                nota_valor = int(match.group(1))
                if 1 <= nota_valor <= 10:
                    nota = nota_valor
                    break
        
        if nota is None:
            print("⚠️ Erro: A IA não retornou a nota corretamente!")
            print("Resposta recebida:", resposta)

        # Remove formatação markdown da resposta para exibição
        resposta = re.sub(r'\*\*', '', resposta)  # Remove negrito
        resposta = re.sub(r'\*', '', resposta)    # Remove itálico

        return nota, resposta

    return None, f"Erro ao acessar API: {response.text}"

async def delete_game(game_name: str):
    
    game = games.find_one(
        {"name": {"$regex": f"^{re.escape(game_name)}"}}
    )
    
    if not game:
        return False
    
    result = games.delete_one({"_id": game["_id"]})
    
    if result.deleted_count > 0:
        return game["name"]
    return False    

def extract_criterios(resposta):
    """Extrai os critérios da resposta da IA"""
    import re
    criterios_match = re.search(r'Critérios para Zerar:(.*?)(?=Justificativa da Nota:|$)', resposta, re.DOTALL)
    if criterios_match:
        criterios_text = criterios_match.group(1).strip()
        # Remove marcadores de lista e espaços extras
        criterios = [c.strip().lstrip('*•-') for c in criterios_text.split('\n') if c.strip()]
        return [c for c in criterios if c]  # Remove linhas vazias
    return []

async def get_game_criterios(game_name):
    """Retorna os critérios de um jogo específico."""
    game = games.find_one({"name": {"$regex": re.escape(game_name), "$options": "i"}})
    if game and "criterios" in game:
        return game["criterios"]
    return None    