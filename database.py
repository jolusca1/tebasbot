import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_TOKEN"))
database = client['tebasBot']
users = database['users']

async def newUser(user):
    fill = {"discord_id": user.id}
    if users.count_documents(fill) == 0:
        userObject = {
            "discord_id": user.id,
            "points": 10
        }
        users.insert_one(userObject)
        return userObject
    else:
        return False
    
async def check_points(user):
    await newUser(user)
    
    fill = {"discord_id": user.id}
    result = users.find(fill)
    
    return result.__getitem__(0)["points"]

async def changePoints(user, quantity):
    await newUser(user)
    
    actuallyPoints = await checkPoints(user)
    
    fill = {"discordId": user.id}
    relation = { "$set": {
        "coins": actuallyPoints + quantity                
        }
    }
    
    users.update_one(fill, relation)        