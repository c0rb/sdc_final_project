import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch, FontManager

from query import get_games, get_events, get_teams

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


def plot_defensive_actions(team, events, game_id):
    def_actions = events[events['type_name'].isin(['Duel']) & (
                events['team_id'] == team['team_id'])]
    xy_location = pd.DataFrame(def_actions['location'].to_list(), index=def_actions['location'].index,
                               columns=['x', 'y'])
    duels = pd.concat([def_actions, xy_location], axis=1).reset_index()
    df_extra = pd.json_normalize(duels['extra'])
    df_extra = df_extra.add_prefix('extra.')
    duels = pd.concat([duels, df_extra], axis=1)


    font_url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/abel/Abel-Regular.ttf'
    fm = FontManager(url=font_url)
    pitch = VerticalPitch(pitch_type='statsbomb',
                          goal_type='box',
                          goal_alpha=0.8,
                          pitch_color='#313852',
                          )
    fig, axs = pitch.grid(title_height=0.08, title_space=0,
                          axis=False,
                          grid_height=0.84)
    fig.set_facecolor('#313852')

    successful_duels = duels[
        duels['extra.duel.outcome.name'].isin(['Won', 'Success', 'Success In Play', 'Success Out'])]
    successful_duels_scatter = pitch.scatter(successful_duels.x, successful_duels.y,
                                             edgecolors='black',
                                             c='#a6d639',
                                             s=100,
                                             marker='X',
                                             label='Successful Duel',
                                             ax=axs['pitch'])
    unsuccessful_duels = duels[
        ~duels['extra.duel.outcome.name'].isin(['Won', 'Success', 'Success In Play', 'Success Out'])]
    unsuccessful_duels_scatter = pitch.scatter(unsuccessful_duels.x, unsuccessful_duels.y,
                                             edgecolors='white',
                                             c='#ff0000',
                                             s=100,
                                             marker='P',
                                             label='Unsuccessful Duel',
                                             ax=axs['pitch'])

    legend = axs['pitch'].legend(prop=fm.prop, loc='upper left')
    for text in legend.get_texts():
        text.set_fontsize(15)
    plt.savefig('plots/duels/' + team['team_name'] + "_" + str(game_id) + '.png')

df_games = get_games()
for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        plot_defensive_actions(team, events=df_events, game_id=game_id)
