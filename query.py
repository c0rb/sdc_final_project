import pandas as pd
from pymongo import MongoClient

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
client = MongoClient('mongodb://localhost:27017')
db = client['final_project']
games_collection = db['games']
teams_collection = db['teams']
events_collection = db['events']


def get_teams(game_id):
    query = {'game_id': game_id}
    cursor =  teams_collection.find(query)
    return pd.DataFrame(list(cursor))

def get_games():
    cursor =  games_collection.find({})
    return pd.DataFrame(list(cursor))

def get_events(game_id):
    query = {'game_id': game_id}
    cursor =  events_collection.find(query)
    return pd.DataFrame(list(cursor))