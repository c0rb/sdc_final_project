import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from mplsoccer import VerticalPitch
from query import get_events, get_games, get_teams
from pprint import pprint


def plot_carry_heatmap(team, events, game_id):
    carry = events[(events['type_name'] == "Carry") & (events['team_id'] == team['team_id'])].reset_index()
    xy_location = pd.DataFrame(carry['location'].to_list(), index=carry['location'].index, columns=['x', 'y'])
    carry = pd.concat([carry, xy_location], axis=1)
    df_extra = pd.json_normalize(carry['extra'])
    df_extra = df_extra.add_prefix('extra.')
    carry = pd.concat([carry, df_extra], axis=1)
    end_xy_location = pd.DataFrame(carry['extra.carry.end_location'].to_list(),
                                   index=carry['extra.carry.end_location'].index,
                                   columns=['end_x', 'end_y'])
    carry = pd.concat([carry, end_xy_location], axis=1)
    # plot(carry, title='All Ball Carries', filename=team['team_name'] + "_" + str(game_id))
    # carry = carry[carry['end_y'] >= carry['y']]
    # plot(carry, title='Forward Ball Carries', filename=team['team_name'] + "_fwd_" + str(game_id))
    for row in carry.itertuples():
        carry.loc[row.Index,'distance'] = math.hypot(abs(row.end_x - row.x), abs(row.end_y - row.y))
    carry_stats =  carry[['game_id', 'player_name', 'distance', 'under_pressure', 'y', 'end_y']].reset_index()
    carry_stats['is_forward'] = carry_stats['end_y'] > carry_stats['y']
    carry_stats['team_name'] = team['team_name']
    return carry_stats

def plot(carry, title, filename):
    plot_x = []
    plot_y = []
    for i, row in carry.iterrows():
        if row['x'] < row['end_x']:
            start_x = row['x']
            end_x = row['end_x']
        else:
            start_x = row['end_x']
            end_x = row['x']
        difference_x = (end_x - start_x) / 10
        start_y = row['y']
        end_y = row['end_y']
        difference_y = (end_y - start_y) / 10
        if (difference_y == 0) or (difference_x == 0):
            x_range = np.array([start_x])
            y_range = np.array([start_y])
        else:
            y_range = np.arange(start_y, end_y, difference_y)
            x_range = np.arange(start_x, end_x, difference_x)
        for i in x_range:
            plot_x.append(i)
        for i in y_range:
            plot_y.append(i)
    pitch = VerticalPitch(line_color='#000009', pitch_type='statsbomb', line_zorder=2)
    fig, axs = pitch.grid(figheight=10, title_height=0.08, endnote_space=0, title_space=0,
                          axis=False,
                          grid_height=0.82)
    kde = pitch.kdeplot(plot_x, plot_y, ax=axs['pitch'],
                        # fill using 100 levels so it looks smooth
                        fill=True, levels=100,
                        # shade the lowest area so it looks smooth
                        # so even if there are no events it gets some color
                        thresh=0,
                        cut=4,  # extended the cut so it reaches the bottom edge
                        cmap='Blues')
    axs['pitch'].set_title(title, size=15)
    plt.savefig('plots/carry/' + filename + '.png')


df_games = get_games()
df_stats = pd.DataFrame()
for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        df_carry_stats = plot_carry_heatmap(team, events=df_events, game_id=game_id)
        df_stats = pd.concat([df_stats, df_carry_stats], ignore_index=True)
df_stats.to_csv('csv/carry/stats.csv', mode='a', header=True,
                encoding='utf-8', sep=',')
