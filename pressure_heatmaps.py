import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from mplsoccer import VerticalPitch
from query import get_events, get_games, get_teams


def plot_pressure_heatmap(team, events, game_id):
    pressure = events[(events['type_name'] == "Pressure") & (events['team_id'] == team['team_id'])].reset_index()
    xy_location = pd.DataFrame(pressure['location'].to_list(), index=pressure['location'].index, columns=['x', 'y'])
    pressure = pd.concat([pressure, xy_location], axis=1)
    path_eff = [path_effects.Stroke(linewidth=3, foreground='black'),
                path_effects.Normal()]
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#313852')
    fig, axs = pitch.grid(title_height=0.08, title_space=0,
                          # Turn off the endnote/title axis. I usually do this after
                          # I am happy with the chart layout and text placement
                          axis=False,
                          grid_height=0.84)
    fig.set_facecolor('#313852')
    # heatmap and labels
    bin_statistic = pitch.bin_statistic_positional(pressure.x, pressure.y, statistic='count',
                                                   positional='full', normalize=True)
    pitch.heatmap_positional(bin_statistic, ax=axs['pitch'],
                             cmap='inferno', edgecolors='#22312b')
    labels = pitch.label_heatmap(bin_statistic, color='#f4edf0', fontsize=18,
                                 ax=axs['pitch'], ha='center', va='center',
                                 str_format='{:.0%}', path_effects=path_eff)
    plt.savefig('plots/pressing/' + team['team_name'] + "_" + str(game_id) + '.png')


df_games = get_games()
for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        plot_pressure_heatmap(team, events=df_events, game_id=game_id)