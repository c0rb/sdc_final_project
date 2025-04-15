from mplsoccer import VerticalPitch
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt

def plot_pass_into_final_third(df, team_name, game_id):
    path_eff = [path_effects.Stroke(linewidth=3, foreground='black'),
                path_effects.Normal()]
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#313852',
                          half=True, pad_bottom=-15, line_color='black')
    fig, axs = pitch.grid(title_height=0.08, title_space=0,
                          axis=False,
                          grid_height=0.84)
    fig.set_facecolor('#313852')
    # heatmap and labels
    bin_statistic = pitch.bin_statistic(df.end_x, df.end_y, statistic='count',
                                                   bins=[6,5], normalize=True)
    pitch.heatmap(bin_statistic, ax=axs['pitch'],
                             cmap='afmhot', edgecolors='#313852', alpha=0.6)
    labels = pitch.label_heatmap(bin_statistic, color='#f4edf0', fontsize=18,
                                 ax=axs['pitch'], ha='center', va='center',
                                 str_format='{:.0%}', path_effects=path_eff)
    pitch.annotate(
        text='Distribution of passes in final third (light / higher percentage = more)',
        xy=(0.25, 0.5), xycoords='axes fraction', fontsize=15, color='white', ha='center', va='center',
        fontfamily="Monospace", ax=axs['title']
    )
    plt.savefig('plots/passes/final_percentage/' + team_name + "_" + str(game_id) + '.png')
