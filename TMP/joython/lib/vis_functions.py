# Library dedicated to produce templates of plots to be used later on
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

def horizontal_subplots(x,ys,yer,legend):
    colors=list(mcolors.TABLEAU_COLORS.keys())
    fig, axs = plt.subplots(dpi=200,ncols=len(legend),figsize=[10,3],sharey=True)
    plt.suptitle("Pedestal Noise level over Runs", fontsize=14)
    fig.subplots_adjust(wspace=0)

    for i in range(len(legend)):
        axs[i].errorbar (x,ys[i], yerr=[yer[i],yer[i]],color= colors[i],linewidth=0,marker='o',markersize=1,elinewidth=1,capsize=2)
        # axs[i].set_ylim([2,10])
        axs[i].legend([legend[i]])
        axs[i].grid()
    return fig,axs
