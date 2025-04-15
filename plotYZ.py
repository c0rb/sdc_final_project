from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

def plotYZshots(df, team, game_id):
    # Create figure
    fig=plt.figure(facecolor='#22312b')
    fig.set_size_inches(12, 4.2)
    #Goal post lines
    plt.plot([34,46],[0,0], color='#c7d5cc', linewidth=1.5)
    plt.plot([36,44],[2.8,2.8], color='#c7d5cc', linewidth=3)
    plt.plot([44,44],[0,2.8], color='#c7d5cc', linewidth=3)
    plt.plot([36,36],[0,2.8], color='#c7d5cc', linewidth=3)
    #Goal net
    plt.gca().add_patch(Rectangle((36, 0), 8, 2.8, fill=False, edgecolor='#c7d5cc', hatch='+', alpha=0.2))
    #Tidy Axes
    plt.axis('off')
    goal_mask = df['extra.shot.outcome.name'] == 'Goal'
    no_goal_mask = df['extra.shot.outcome.name'] != 'Goal'
    sc1 = plt.scatter(df[no_goal_mask].end_y, df[no_goal_mask].end_z, marker='o', color='#ba4f45', label='No Goal')
    sc2 = plt.scatter(df[goal_mask].end_y, df[goal_mask].end_z, marker='o', color='#ad993c', label='Goal')
    plt.ylim(ymin=-0.2, ymax=4)
    plt.xlim(xmin=34, xmax=46)
    plt.legend()
    plt.savefig('plots/shots/' + team['team_name'] + "_YZ_" + str(game_id) + '.png')
