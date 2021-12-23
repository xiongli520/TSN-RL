import matplotlib.pyplot as plt

def paths_process(paths):
    paths_pro = []
    for i in range(len(paths)):
        paths_pro_i = []
        for j in range(len(paths[i])):
            start = paths[i][j][0]/ 10000.
            length = paths[i][j][2] / 10000.
            out = (start,length)
            paths_pro_i.append(out)
        paths_pro.append(paths_pro_i)
    return paths_pro

def plot_paths(paths_pro):

    fig, ax = plt.subplots()
    ls = list(range(1, 124, 2))
    for i in range(62):
        ax.broken_barh(paths_pro[i], (ls[i], 1),
                       facecolors=('tab:orange', 'tab:green', 'tab:red', 'tab:blue', 'tab:pink'))
    #ax.set_ylim(0, 35)
    #ax.set_xlim(0, 200)
    ax.set_xlabel('哈哈哈哈哈哈')
    ls = list(range(1,124,2))
    ax.set_yticks(ls)
    #ax.set_yticklabels(['path[0]', 'path[1]'])
    # ax.grid(True)
    # ax.annotate('race interrupted', (61, 25),
    #             xytext=(0.8, 0.9), textcoords='axes fraction',
    #             arrowprops=dict(facecolor='black', shrink=0.05),
    #             fontsize=16,
    #             horizontalalignment='right', verticalalignment='top')

    plt.show()