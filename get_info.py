from pprint import pprint

from query import get_games, get_teams, get_events

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)

def plot_passes(team, events, game_id):
    df_tactics = events[(events['type_name'] == 'Tactical Shift') & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_tactics['extra'])
    df_tactics = pd.concat([df_tactics, df_extra], axis=1)
    lineup = pd.json_normalize(df_tactics['tactics.lineup'])
    pprint(pd.json_normalize(lineup.iloc[0]))

df_games = get_games()
# pprint(df_games.sample())
game_info = df_games[['game_id', 'home_team_id', 'away_team_id', 'home_score', 'away_score', 'game_day']]
game_info.to_csv('csv/games.csv', mode='a', header=True, encoding='utf-8', index=False, sep=',')