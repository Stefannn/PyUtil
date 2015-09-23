'''
@author Stefan Hegglin
Utilities to plot and analyse profiling information
generated by cProfile using e.g.
python -m cProfile -o output.txt script.py
'''
from __future__ import division
import numpy as np
import pandas as pd
try:
    import seaborn as sns
    sns.set_color_codes("pastel")
    sns.set(style="whitegrid")
    sns.set_context("talk") # bigger fonts etc.
except:
    ImportError('seaborn not found, plotting not available')
import matplotlib.pyplot as plt
import cProfile
import pstats

def load_file(filename):
    '''
    Loads the file specified by filename into a pstats object
    Strips the extraneous path from the module names
    '''
    try:
        return pstats.Stats(filename).strip_dirs()
    except IOError:
        raise

def barplot_top_n_functions(df, n, sort_criterium='tot_time', show_std=True):
    '''
    Barplot of the n most time consuming functions (sorted by sort_criterium)
    df: panda dataframe (e.g. via get_df_from_stats())
    ci: confidence intervall, set to None if you don't want them
    returns: figure
    '''
    tt = ('tot_time', 'mean')
    s_c = (sort_criterium, 'mean') # sort criterium including mean
    total_time = df[tt].sum()
    data = df.sort(columns=[s_c], ascending=False).iloc[0:n]
    topn_time = data[tt].sum()
    frac_time = topn_time / total_time
    if show_std:
        errs = data[(sort_criterium, 'std')]
    else:
        errs = None

    f, ax = plt.subplots(figsize=(10,5))
    sns.barplot(data=data, x=s_c, y='flf', color='b', xerr=errs)
    sns.despine(left=True, bottom=True)
    ax.set(ylabel="", xlabel=sort_criterium + " [s]")
    # write the fraction of total time spent in these n functions
    rect = ax.patches[0] # last rectangle to get position of text
    txt = str(int(100*frac_time)) + "% of total runtime"
    ax.text(rect.get_width()*0.7, rect.get_height()*1.5, txt,
            ha="center", va="center")

    plt.tight_layout()
    return f


def get_df_from_stats(stats):
    ''' Create a panda dataframe out of a Stats class (pstats)'''
    rows = []
    columns = ["ncalls", "pcalls", "tot_time", "tot_time_per",
               "cum_time", "cum_time_per", "file", "line", "function", "flf"]
    for k, v in stats.stats.items():
        fl = k[0]
        line = int(k[1])
        func = k[2]
        pcalls = v[0] # primitive number of calls (excluding recursive calls)
        ncalls = v[1] # total number of calls (including recursive calls)
        assert (pcalls <= ncalls)
        tot_time = v[2]
        cum_time = v[3]
        tot_time_per = v[2] / v[0] if v[0] > 0 else 0
        cum_time_per = v[3] / v[0] if v[0] > 0 else 0
        rows.append(
            [ncalls, pcalls, tot_time, tot_time_per,
             cum_time, cum_time_per, fl, line, func,
             str(fl) + ':' + str(line) + '\n' + str(func) + '()'])
    df = pd.DataFrame(rows, columns=columns)
    return df

def aggregate_profiling_df(df):
    ''' Take a panda dataframe containing profiling information
    eg via ProfilerWithStatistics.run() and aggregate the results over
    the different runs (on the flf column)
    '''
    df = df.groupby(['flf'], as_index=False).agg([np.mean, np.std, 'count'])
    df = df.reset_index()
    return df

class ProfilerWithStatistics(object):
    ''' A profiling class which runs a specified function several times and
    computes the standard deviation of each entry
    '''

    def __init__(self, n_reps=10):
        self.n_reps = n_reps

    def run(self, function_name, *args, **kwargs):
        ''' Profile the function and, create statistics and add std
        Run the desired function self.n_reps times and store the result
        in a common pandas dataframe. If the data gets plotted with barplot,
        sns automatically generates the std of the rows with the same flf.
        Alternatively call aggregate_profiling_df()
        '''
        first_run = True
        for rep in xrange(self.n_reps):
            pr = cProfile.Profile()
            pr.enable()
            function_name(*args, **kwargs)
            pr.disable()
            if first_run:
                df = get_df_from_stats(pstats.Stats(pr).strip_dirs())
                first_run = False
            else:
                df_tmp = get_df_from_stats(pstats.Stats(pr).strip_dirs())
                df = pd.concat([df, df_tmp],
                                ignore_index=True)

        return df, pstats.Stats(pr).strip_dirs()
