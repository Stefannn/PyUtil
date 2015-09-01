'''
Various functions/classes to change matplotlit plots
@author Stefan Hegglin
'''

def set_label_size(ax, fontsize=14):
    ''' Sets xticks, yticks, xlabel, ylabel to fontsize
        ax: matplotlib AxesSubplot
     '''
    for lab in (ax.get_xticklabels() + ax.get_yticklabels() + [ax.xaxis.label]
        + [ax.yaxis.label]):
        lab.set_fontsize(fontsize)
