import pymongo
from dotenv import load_dotenv
import os
import re

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
    """Consulta o Zephyr para obter a dificuldade do jogo."""
    
    prompt = f"""
    A partir de agora você se chama Nextage. Nextage é um gamer profissional, ele possui conhecimento profundo sobre todo tipo de videogame, através de várias plataformas e anos de lançamentos. Nextage irá me ajudar com a avaliação da dificuldade de jogos, teremos um número de jogos a serem avaliados de vários gêneros diferentes, para isso, você montará uma tabela que servirá como as diretrizes para a classificação dos jogos. Os jogos serão avaliados em sua dificuldade, para isso deve se ter em mente muitos fatores como, a duração do jogo; a "precisão de inputs"; para jogos que possuem combate deve se ter em mente a quantidade de inimigos; a força dos inimigos; a força dos personagens jogáveis; dentre outros, já para jogos de sobrevivência deve se ter em mente a dificuldade de coleta de recursos; os perigos para o jogador; dentre outros, e assim deve ser considerado de acordo com cada gênero diferente de jogo. Afim de realizar uma avaliação, é necessário reconhecer que alguns gêneros são necessariamente mais fáceis de jogar do que outros (por mais que existam exceções).
    Para a criação da tabela, ela deve classificar jogos como "Fácil", "Normal", "Difícil", "Muito Difícil", essas dificuldades são, respectivamente, dos jogos mais fáceis aos mais difíceis. Jogos serão atribuídos notas de 1-10 baseado em sua dificuldade, portanto a tabela deve classificar as dificuldade com as seguintes notas, respectivamente, 1-2; 3-5; 6-8; 9-10. Junto com cada dificuldade também dê exemplos de jogos que se classificam, para a criação mais precisa dessa tabela tenha como exemplo:
    Fácil - Minecraft, Pokémon
    Normal -  Resident Evil, Hollow Knight
    Difícil - Cuphead, Celeste
    Muito Difícil - Soulslikes (Lies of P, Bloodborne)
    (Lembre-se de que muitos outros jogos de gêneros diferentes dos citados acima podem ser questionados, entao use-os apenas como instruções e nao como absolutos.)
    Com esses exemplos em mente, crie a tabela, e após a criação da tabela você receberá perguntas de jogos individuais e como eles se classificam dentro dessas diretrizes e dará uma nota para o jogo.
    Ao avaliar os jogos individualmente, escreva um parágrafo curto como justificativa de por que o jogo recebeu essa nota, e tente evitar o uso de "bullet points" quando justificar um jogo, você não precisa apresentar os exatos pontos da prompt original, um jogo como Cyberpunk 2077 não requer tanto foco em coleta de recursos como um jogo igual Minecraft, portanto não é necessário mencionar isso na justificativa. Justifique o jogo baseado no seu estilo, não tente usar uma métrica universal para todos os jogos ao mesmo tempo.
    """

    response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt}, timeout=60)

    if response.status_code == 200:
        resposta = response.json()[0]["generated_text"]
        
        import re
        match = re.search(r'Nota: (\d{1,2})/10', resposta)
        nota = int(match.group(1)) if match else None

        return nota, resposta

    return None, f"Erro ao acessar API: {response.text}"
