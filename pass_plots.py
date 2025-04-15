import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from query import get_events, get_games, get_teams
import matplotlib.pyplot as plt
import numpy

from mplsoccer import Pitch

def plot_passes(team, events, game_id):
    df_passes = events[(events['type_name'] == "Pass") & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_passes['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_team_passes = pd.concat([df_passes, df_extra], axis=1)
    df_team_passes.astype({'extra.pass.outcome.name': 'string',})
    xy_location = pd.DataFrame(df_team_passes['location'].to_list(), index=df_team_passes['location'].index,
                              columns=['x', 'y'])
    df_team_passes = pd.concat([df_team_passes, xy_location], axis=1)

    end_xy_location = pd.DataFrame(df_team_passes['extra.pass.end_location'].to_list(), index=df_team_passes['extra.pass.end_location'].index,
                              columns=['end_x', 'end_y'])
    df_team_passes = pd.concat([df_team_passes, end_xy_location], axis=1)

    # df_team_passes = df_team_passes[(df_team_passes['extra.pass.angle'] >= (-3.14/2)) & (df_team_passes['extra.pass.angle'] <= (3.14/2)) & (df_team_passes['extra.pass.type.name'].isna())]
    # df_corners = df_team_passes[df_team_passes['extra.pass.type.name'] == 'Corner']
    df_free_kicks = df_team_passes[df_team_passes['extra.pass.type.name'] == 'Free Kick']
    # df_into_final_third = df_team_passes[df_team_passes['end_x'] >= 90]
    # plot_pass_into_final_third(df_into_final_third, team['team_name'], game_id)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#313852', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(16, 9), constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#313852')

    df_to_plot = df_free_kicks
    succesful_passes = df_to_plot[numpy.isnan(df_to_plot['extra.pass.outcome.id'])]
    # Plot the completed passes
    lc1 = pitch.lines(succesful_passes.x, succesful_passes.y,
                      succesful_passes.end_x,
                      succesful_passes.end_y,
                      lw=5, transparent=True, comet=True, label='completed passes',
                      color='#ad993c', ax=ax)
    other_passes = df_to_plot[~numpy.isnan(df_to_plot['extra.pass.outcome.id'])]
    # Plot the other passes
    lc2 = pitch.lines(other_passes.x, other_passes.y,
                      other_passes.end_x,
                      other_passes.end_y,
                      lw=5, transparent=True, comet=True, label='other passes',
                      color='#ba4f45', ax=ax)


    ax.legend(facecolor='white', edgecolor='None', fontsize=20, loc='upper left', handlelength=4)
    plt.savefig('plots/passes/freekick/' + team['team_name'] + "_" + str(game_id) + '.png')

df_games = get_games()


for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        plot_passes(team, events=df_events, game_id=game_id)

