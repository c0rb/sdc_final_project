from mplsoccer import VerticalPitch, FontManager

from query import get_games, get_events, get_teams
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)


def plot_defensive_actions(team, events, game_id):
    def_actions = events[events['type_name'].isin(['Interception', 'Block', 'Duel', 'Ball Recovery']) & (
            events['team_id'] == team['team_id'])]
    xy_location = pd.DataFrame(def_actions['location'].to_list(), index=def_actions['location'].index,
                               columns=['x', 'y'])
    def_actions = pd.concat([def_actions, xy_location], axis=1)
    interceptions = def_actions[def_actions['type_name'] == 'Interception'].reset_index()
    df_extra = pd.json_normalize(interceptions['extra'])
    df_extra = df_extra.add_prefix('extra.')
    interceptions = pd.concat([interceptions, df_extra], axis=1)

    duels = def_actions[def_actions['type_name'] == 'Duel'].reset_index()
    df_extra = pd.json_normalize(duels['extra'])
    df_extra = df_extra.add_prefix('extra.')
    duels = pd.concat([duels, df_extra], axis=1)

    blocks = def_actions[def_actions['type_name'] == 'Block'].reset_index()
    recoveries = def_actions[def_actions['type_name'] == 'Ball Recovery'].reset_index()
    actions_by_player = blocks.groupby(['player_name', 'game_id']).size().to_frame(name='block_amount').reset_index()
    actions_by_player = actions_by_player.merge(
        recoveries.groupby(['player_name', 'game_id']).size().to_frame(name='recoveries_amount').reset_index(),
        left_on=['player_name', 'game_id'],
        right_on=['player_name', 'game_id'], how='outer').fillna(0)
    actions_by_player = actions_by_player.merge(
        interceptions.groupby(['player_name', 'game_id']).size().to_frame(name='interceptions_amount').reset_index(),
        left_on=['player_name', 'game_id'],
        right_on=['player_name', 'game_id'], how='outer').fillna(0)
    actions_by_player = actions_by_player.merge(
        duels.groupby(['player_name', 'game_id']).size().to_frame(name='duels_amount').reset_index(),
        left_on=['player_name', 'game_id'],
        right_on=['player_name', 'game_id'], how='outer').fillna(0)
    actions_by_player['team_name'] = team['team_name']
    pprint(actions_by_player)
    font_url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/abel/Abel-Regular.ttf'
    fm = FontManager(url=font_url)
    pitch = VerticalPitch(pitch_type='statsbomb',
                          goal_type='box',
                          goal_alpha=0.8,
                          pitch_color='#313852',
                          pad_top=20
                          )
    fig, axs = pitch.grid(title_height=0.08, title_space=0,
                          axis=False,
                          grid_height=0.84)
    fig.set_facecolor('#313852')
    blocks_scatter = pitch.scatter(blocks.x, blocks.y,
                                   edgecolors='black',  # give the markers a charcoal border
                                   c='#ffec00',  # no facecolor for the markers
                                   s=100,
                                   marker='p',
                                   label='Block',
                                   ax=axs['pitch'])
    recoveries_scatter = pitch.scatter(recoveries.x, recoveries.y,
                                       edgecolors='white',  # give the markers a charcoal border
                                       c='#6d3875',  # no facecolor for the markers
                                       s=100,
                                       marker='^',
                                       label='Recovery',
                                       ax=axs['pitch'])
    successful_duels = duels[
        duels['extra.duel.outcome.name'].isin(['Won', 'Success', 'Success In Play', 'Success Out'])]
    successful_duels_scatter = pitch.scatter(successful_duels.x, successful_duels.y,
                                             edgecolors='black',  # give the markers a charcoal border
                                             c='#a6d639',  # no facecolor for the markers
                                             s=100,
                                             marker='d',
                                             label='Successful Duel',
                                             ax=axs['pitch'])
    successful_interceptions = interceptions[
        interceptions['extra.interception.outcome.name'].isin(['Won', 'Success', 'Success In Play', 'Success Out'])]
    successful_interceptions_scatter = pitch.scatter(successful_interceptions.x, successful_interceptions.y,
                                             edgecolors='black',  # give the markers a charcoal border
                                             c='#d44242',  # no facecolor for the markers
                                             s=100,
                                             marker='X',
                                             label='Successful Interception',
                                             ax=axs['pitch'])
    legend = axs['pitch'].legend(prop=fm.prop, loc='upper left')
    for text in legend.get_texts():
        text.set_fontsize(15)
    plt.savefig('plots/defensive_actions/' + team['team_name'] + "_" + str(game_id) + '.png')
    return actions_by_player

df_games = get_games()
df_stats = pd.DataFrame(
    columns=['player_name', 'game_id', 'block_amount', 'recoveries_amount', 'interceptions_amount', 'duels_amount'])
for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        df_stats_per_game=plot_defensive_actions(team, events=df_events, game_id=game_id)
        df_stats = pd.concat([df_stats, df_stats_per_game], ignore_index=True)
df_stats.to_csv('csv/defensive_actions/stats.csv', mode='a', header=True, encoding='utf-8', index=False, sep=',')
