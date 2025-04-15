import numpy as np
import pandas as pd

from plotYZ import plotYZshots

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from query import get_events, get_games, get_teams
from mplsoccer import VerticalPitch, FontManager
import matplotlib.pyplot as plt


def get_label(df):
    if df['extra.shot.outcome.name'] == 'Blocked':
        return 'Blocked'
    if df['extra.shot.type.name'] == 'Corner':
        return 'From Corner'
    if df['extra.shot.type.name'] == 'Free Kick':
        return 'From Free Kick'
    return 'No Goal'


def plot_shots(team, events, game_id):
    df_shots = events[events['type_name'] == 'Shot']
    df_team_shots = df_shots[df_shots['team_id'] == team['team_id']].reset_index()
    df_extra = pd.json_normalize(df_team_shots['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_team_shots = pd.concat([df_team_shots, df_extra], axis=1)
    df_team_shots = df_team_shots.drop('extra', axis=1)
    xy_location = pd.DataFrame(df_team_shots['location'].to_list(), index=df_team_shots['location'].index,
                               columns=['x', 'y'])
    df_team_shots = pd.concat([df_team_shots, xy_location], axis=1)
    df_team_shots = df_team_shots.drop('location', axis=1)
    end_xy_location = pd.DataFrame(df_team_shots['extra.shot.end_location'].to_list(),
                                   index=df_team_shots['extra.shot.end_location'].index,
                                   columns=['end_x', 'end_y', 'end_z'])
    df_team_shots = pd.concat([df_team_shots, end_xy_location], axis=1)
    df_team_shots = df_team_shots.drop('extra.shot.end_location', axis=1)
    blocked = df_team_shots['extra.shot.outcome.name'] == 'Blocked'
    corner = df_team_shots['extra.shot.type.name'] == 'Corner'
    freekick = df_team_shots['extra.shot.type.name'] == 'Free Kick'
    goal = df_team_shots['extra.shot.outcome.name'] == 'Goal'
    df_team_shots['shot.color'] = np.select([blocked, corner, freekick, goal], ['red', '#62c462', '#12dff3', '#b94b75'],
                                            'white')
    df_team_shots['shot.label'] = np.select([blocked, corner, freekick, goal],
                                            ['Blocked', 'From Corner', 'From Free Kick', 'Goal'], 'No Goal')
    df_team_shots = df_team_shots[(df_team_shots['extra.shot.type.id'] != 88)]

    df_team_shots['game_id'] = game_id
    shots_per_player_xg = df_team_shots[['player_name', 'extra.shot.type.name', 'extra.shot.outcome.name', 'extra.shot.statsbomb_xg', 'team_name','game_id']].groupby(
        ['player_name', 'extra.shot.type.name', 'extra.shot.outcome.name', 'team_name','game_id']).agg(["count","max", "sum"])

    goals = df_team_shots[goal]

    font_url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/abel/Abel-Regular.ttf'
    fm = FontManager(url=font_url)
    pitch = VerticalPitch(pitch_type='statsbomb',
                          half=True,  # half of a pitch
                          goal_type='box',
                          goal_alpha=0.8,
                          pitch_color='#22312b')
    fig, ax = pitch.grid(grid_width=0.85, left=0.15, figheight=10,axis=False,grid_height=1, title_height=0, endnote_height=0)

    for index, row in df_team_shots.iterrows():
        pitch.arrows(xstart=row.x, ystart=row.y, xend=row.end_x,
                     yend=row.end_y,
                     edgecolors='black',
                     width=2,
                     alpha=0.6,
                     color=row['shot.color'],
                     ax=ax)
        pitch.scatter(row.x, row.y,
                      s=(row['extra.shot.statsbomb_xg'] * 900) + 100,
                      edgecolors='black',  # give the markers a charcoal border
                      c=row['shot.color'],  # no facecolor for the markers
                      marker='football',
                      label=row['shot.label'] + ' xG: ' + str(round(row['extra.shot.statsbomb_xg'],2)),
                      ax=ax)

    if goals.shape[0] > 0:
        for i, goal in goals.iterrows():
            count = goals[(goals['x'] == goal['x']) & (goals['y'] == goal['y'])].shape[0]
            y = goal['x'] - 2, goal['y'] - 2 - 1 * goal['extra.shot.statsbomb_xg'] - 1 * (count - 1)
            pitch.annotate(str(goal['player_name']), y,
                           ax=ax, color='#b94b75')
    # adding a legend
    legend = fig.legend(prop=fm.prop, loc='upper left', markerscale=0.8)
    for text in legend.get_texts():
        text.set_fontsize(18)
    plt.savefig('plots/shots/' + team['team_name'] + "_" + str(game_id) + '.png')

    plotYZshots(df_team_shots, team, game_id)
    return shots_per_player_xg.reset_index()

df_games = get_games()
df_stats = pd.DataFrame(columns=['player_name', 'extra.shot.type.name', 'extra.shot.outcome.name','team_name','game_id', 'shot_count', 'xG_max', 'xG_total'])
for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        df_stats_per_game=plot_shots(team, events=df_events, game_id=game_id)
        df_stats = pd.concat([df_stats, df_stats_per_game], ignore_index=True)
df_stats.to_csv('csv/shots/shots.csv', mode='a', header=True,
                            encoding='utf-8', sep=',')