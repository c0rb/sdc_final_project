import pandas as pd
from pprint import pprint

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1200)
from query import get_events, get_games, get_teams
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mplsoccer import VerticalPitch


def add_arrow(x1,y1,x2,y2,ax,
              **kwargs
              ):
    ax.plot([x1, x2],[y1, y2],**kwargs)

    annotation = ax.annotate("",
                             xytext=(x1, y1),
                             xy=(x1 + ((x2 - x1) / 2),
                                 y1 + ((y2 - y1) / 2)
                                 ),
                             arrowprops=dict(arrowstyle="->", **kwargs),
                             zorder=10,
                             size=30,
                             label="Darker color indicates higher number of passes in that direction"
                             )

    return annotation


def plot_passes(team, events, game_id):
    df_startingXI = events[(events['type_name'] == 'Starting XI') & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_startingXI['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_startingXI = pd.concat([df_startingXI, df_extra], axis=1)
    df_startingXI = df_startingXI[['minute', 'second', 'extra.tactics.formation']]

    df_tactics = events[
        (events['type_name'] == 'Tactical Shift') & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_tactics['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_tactics = pd.concat([df_tactics, df_extra], axis=1)
    pprint(df_tactics.columns.to_list())
    df_tactics = df_tactics.reindex(columns=['minute', 'second', 'extra.tactics.formation'])

    df_passes = events[(events['type_name'] == "Pass") & (events['team_id'] == team['team_id'])].reset_index()
    df_extra = pd.json_normalize(df_passes['extra'])
    df_extra = df_extra.add_prefix('extra.')
    df_team_passes = pd.concat([df_passes, df_extra], axis=1)
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

    df_tactics_time = pd.concat([df_startingXI, df_tactics[df_tactics['minute'] < 90]], ignore_index=True).reset_index()
    pprint(str(game_id) + ' ' + str(team['team_name']))
    pprint(df_tactics_time)
    size = df_tactics_time.shape[0]
    pprint('size ' + str(size))
    nrcols = size
    nrrows = 1
    if size == 4:
        nrcols = 2
        nrrows = 2
    fig, axes = VerticalPitch().draw(nrows=nrrows, ncols=nrcols, figsize=(16, 10))
    fig.set_facecolor("white")

    cmap = plt.cm.get_cmap('Reds')

    pprint('total ' + str(df_team_passes.shape[0]))
    for k, row in df_tactics_time.iterrows():
        ax = axes
        pprint('k ' + str(k))
        df_passes_in_timeframe = df_team_passes[
            df_team_passes['minute'] * 60 + df_team_passes['second'] > row['minute'] * 60 + row['second']]
        if (size > 1) and (size != 4):
            ax = axes[k]
        if size == 4:
            ax = axes[int(k / 2)][int(k % 2)]
        if size > 1:
            if k < size - 1:
                next = df_tactics_time.iloc[k + 1]
                pprint(row)
                df_passes_in_timeframe = df_passes_in_timeframe[
                    df_passes_in_timeframe['minute'] * 60 + df_passes_in_timeframe['second'] < next['minute'] * 60 +
                    next['second']]

        pprint('team passes ' + str(df_passes_in_timeframe.shape[0]))
        df_player_locations = df_passes_in_timeframe.groupby(['player_name']).agg(x=('x', 'mean'), y=('y', 'mean'),
                                                                                  total=('x', 'size')).reset_index()

        df_players_passes = df_passes_in_timeframe.groupby(['player_name', 'extra.pass.recipient.name']).agg(
            passes=('x', 'size')).reset_index()

        # some pandas merging to get all useful data in a single # df
        df_players_passes = df_players_passes.merge(df_player_locations[['player_name', 'x', 'y']],
                                                    left_on='player_name',
                                                    right_on='player_name').rename(
            columns={'x': 'passer_x', 'y': 'passer_y'})

        df_players_passes = df_players_passes.merge(df_player_locations[['player_name', 'x', 'y']],
                                                    left_on='extra.pass.recipient.name', right_on='player_name').rename(
            columns={'x': 'recipient_x', 'y': 'recipient_y', 'player_name_x': 'player',
                     'extra.pass.recipient.name': 'pass_recipient'})
        df_players_passes.drop('player_name_y', axis=1, inplace=True)
        df_players_passes.sort_values("passes", ascending=True, inplace=True)

        highest_passes = df_players_passes['passes'].max()
        df_players_passes['passes_scaled'] = df_players_passes['passes'] / highest_passes

        df_player_to_player = df_players_passes[['player', 'pass_recipient', 'passes']]

        inverse_rows = []
        for pass_row in df_player_to_player.itertuples():
            if pass_row.Index not in inverse_rows:
                inverse_pass_row =  df_player_to_player[(df_player_to_player['player'] == pass_row.pass_recipient) & (df_player_to_player['pass_recipient'] == pass_row.player)]
                if not inverse_pass_row.empty:
                    inverse_rows.append(inverse_pass_row.index)
                    df_player_to_player.loc[pass_row.Index,'reverse_passes'] = inverse_pass_row['passes'].iloc[0]
                    df_player_to_player.loc[pass_row.Index,'total_passes'] = pass_row.passes + inverse_pass_row['passes'].iloc[0]
                else:
                    df_player_to_player.loc[pass_row.Index,'reverse_passes'] = 0
                    df_player_to_player.loc[pass_row.Index,'total_passes'] = pass_row.passes
            else:
                df_player_to_player = df_player_to_player.drop(pass_row.Index)
        df_player_to_player = df_player_to_player.sort_values('total_passes', ascending=False, ignore_index=True)
        df_player_to_player['team_name'] = team['team_name']
        df_player_to_player['game_id'] = game_id
        df_player_to_player.to_csv('csv/passes/passing_links.csv', mode='a', header=True,
                            encoding='utf-8', index=False)
        pprint(df_player_to_player.shape)
        annotations = []
        LABEL = True
        for pass_row in df_players_passes.itertuples():
            if pass_row.passes > 0:

                if abs(pass_row.recipient_y - pass_row.passer_y) > abs(pass_row.recipient_x - pass_row.passer_x):
                    if pass_row.player > pass_row.pass_recipient:
                        x_shift, y_shift = 0, 2
                    else:
                        x_shift, y_shift = 0, -2
                else:
                    if pass_row.player > pass_row.pass_recipient:
                        x_shift, y_shift = 2, 0
                    else:
                        x_shift, y_shift = -2, 0

                arrow = add_arrow(x1=pass_row.recipient_y + y_shift,
                                  y1=pass_row.recipient_x + x_shift,
                                  x2=pass_row.passer_y + y_shift,
                                  y2=pass_row.passer_x + x_shift,
                                  ax=ax,
                                  color=cmap(pass_row.passes_scaled),
                                  alpha=pass_row.passes_scaled,
                                  lw=pass_row.passes_scaled * 3)

                annotations.append(arrow)

        texts = []

        df_player_locations.sort_values("total", ascending=True, inplace=True)

        for location_row in df_player_locations.itertuples():
            ax.scatter(location_row.y,
                       location_row.x,
                       s=(location_row.total / df_player_locations.total.max()) * 700,
                       fc='white',
                       ec='red',
                       lw=5,
                       zorder=100,
                       label="Size indicates total passes made by player" if LABEL else ""
                       )
            text = ax.text(location_row.y,
                           location_row.x - 4,
                           ha='center',
                           va='center',
                           zorder=200,
                           s=location_row.player_name)

            text.set_path_effects([pe.PathPatchEffect(offset=(2, -2), hatch='xxxx', facecolor='gray'),
                                   ])
            texts.append(text)

            LABEL = False

        ax.text(0,
                125,
                f"Passes from minute {df_passes_in_timeframe.minute.min()}-{df_passes_in_timeframe.minute.max()} Tactics: {str(int(row['extra.tactics.formation']))}",
                fontsize=15,
                va='top', )

        ax.text(80,
                -2,
                f"Minimum Passes: {1}",
                fontsize=15,
                va='top',
                ha='right',
                )

    plt.savefig('plots/passes/network/' + team['team_name'] + "_" + str(game_id) + '.png')



df_games = get_games().sample()

for i, game in df_games.iterrows():
    game_id=game['game_id']
    df_events = get_events(game_id)
    df_teams = get_teams(game_id)
    for j, team in df_teams.iterrows():
        plot_passes(team, events=df_events, game_id=game_id)
