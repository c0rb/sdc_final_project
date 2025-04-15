import warnings
from statsbombpy.api_client import NoAuthWarning
warnings.simplefilter('ignore', NoAuthWarning)

from socceraction.data.statsbomb import StatsBombLoader
import pandas as pd
from pymongo import MongoClient

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
api = StatsBombLoader(getter="remote", creds=None)
client = MongoClient('mongodb://localhost:27017')
db = client['final_project']
games_collection = db['games']
teams_collection = db['teams']
events_collection = db['events']

df_competitions = api.competitions()
df_games = api.games(competition_id=9, season_id=27)


team_ids = [169,180,185,904]
df_filtered = df_games[df_games['home_team_id'].isin(team_ids) & df_games['away_team_id'].isin(team_ids)]
games_dict = df_filtered.to_dict('records')
games_collection.insert_many(games_dict)

for i, game in df_filtered.iterrows():
    game_id = game['game_id']

    df_events = api.events(game_id)
    events_dict = df_events.to_dict('records')
    events_collection.insert_many(events_dict)

    df_teams = api.teams(game_id=game_id)
    df_teams['game_id'] = game_id
    teams_dict = df_teams.to_dict('records')
    teams_collection.insert_many(teams_dict)
