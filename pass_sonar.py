import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from query import get_events, get_games, get_teams
import matplotlib.pyplot as plt
import matplotlib.patches as pat

from mplsoccer import Pitch


def plot_passes(team, events, game_id):
    df_team_passeses = events[(events['type_name'] == "Pass") & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_team_passeses['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_team_passes = pd.concat([df_team_passeses, df_extra], axis=1)
    df_team_passes.astype({'extra.pass.angle': 'int64',
                           'extra.pass.outcome.name': 'string',
                           })
    xy_location = pd.DataFrame(df_team_passes['location'].to_list(), index=df_team_passes['location'].index,
                               columns=['x', 'y'])
    df_team_passes = pd.concat([df_team_passes, xy_location], axis=1)

    end_xy_location = pd.DataFrame(df_team_passes['extra.pass.end_location'].to_list(),
                                   index=df_team_passes['extra.pass.end_location'].index,
                                   columns=['end_x', 'end_y'])
    df_team_passes = pd.concat([df_team_passes, end_xy_location], axis=1)
    df_team_passes = df_team_passes[(df_team_passes['extra.pass.type.name'].isna())]

    df_team_passes['angle_bin'] = pd.cut(
        df_team_passes['extra.pass.angle'],
        bins=np.linspace(-np.pi, np.pi, 9),
        labels=False,
        include_lowest=True
    )

    sonar_df = df_team_passes.groupby(["player_name", "angle_bin"], as_index=False)
    sonar_df = sonar_df.agg({"extra.pass.length": "mean"})
    pass_amt = df_team_passes.groupby(['player_name', 'angle_bin']).size().to_frame(name='amount').reset_index()
    accurate_passes = df_team_passes[np.isnan(df_team_passes['extra.pass.outcome.id'])].groupby(
        ['player_name', 'angle_bin']).size().to_frame(name='accurate').reset_index()

    sonar_df = pd.concat([sonar_df, pass_amt["amount"]], axis=1)
    sonar_df = pd.concat([sonar_df, accurate_passes["accurate"]], axis=1)
    sonar_df['accurate'].fillna(0)
    sonar_df['acc_percentage'] = sonar_df['accurate'] / sonar_df['amount'] * 100
    average_location = df_team_passes.groupby('player_name').agg({'x': ['mean'], 'y': ['mean']})
    average_location.columns = ['x', 'y']
    sonar_df = sonar_df.merge(average_location, left_on="player_name", right_index=True)


    fig, ax = plt.subplots(figsize=(13, 8), constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#0e1117')
    ax.patch.set_facecolor('#0e1117')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
    pitch.draw(ax=ax)
    startingXI = df_team_passes['player_name'].to_list()
    for player in startingXI:
        player_sonar = sonar_df[sonar_df['player_name'] == player]
        for _, row in player_sonar.iterrows():
            degree_left_start = -180

            color = "#006b71" if row['acc_percentage'] < 25 else "#009ea7" if row['acc_percentage'] < 50 else '#00d5e1' if \
            row['acc_percentage'] < 75 else "#3ff5ff"

            n_bins = 8
            degree_left = degree_left_start + (360 / n_bins) * (row.angle_bin)
            degree_right = degree_left - (360 / n_bins)

            pass_wedge = pat.Wedge(
                center=(row.x, row.y),
                r=row['extra.pass.length'] * 0.16,
                theta1=degree_right,
                theta2=degree_left,
                facecolor=color,
                edgecolor="black",
                alpha=0.6
            )
            ax.add_patch(pass_wedge)

    for _, row in average_location.iterrows():
        if row.name in startingXI:
            annotation_text = row.name

            pitch.annotate(
                annotation_text,
                xy=(row.x, row.y - 4.5),
                c='white',
                va='center',
                ha='center',
                size=9,
                fontweight='bold',
                ax=ax
            )

    pitch.annotate(
        text='Sonar length corresponds to frequency of passes\nSonar color corresponds to pass accuracy (light = more)',
        xy=(0.5, 0.01), xycoords='axes fraction', fontsize=10, color='white', ha='center', va='center',
        fontfamily="Monospace", ax=ax
    )
    plt.savefig('plots/passes/sonar/' + team['team_name'] + "_" + str(game_id) + '.png')

df_games = get_games()

for i, game in df_games.iterrows():
    game_id = game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        plot_passes(team, events=df_events, game_id=game_id)
