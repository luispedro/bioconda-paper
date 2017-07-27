from matplotlib import pyplot as plt
import datetime
import numpy as np
import seaborn as sns
import pandas as pd

sns.set_style('white')

try:
    log = snakemake.input.log
    pkg = snakemake.input.pkg
    outfile = snakemake.output[0]
except NameError:
    # run in the scripts dir for interactive clicking of points
    log = '../git-log/parsed-log.tsv'
    pkg = '../package-data/all.tsv'
    outfile = None

c = pd.read_table(log)
d = pd.read_table(pkg)

s = c.apply(lambda x: pd.Series(list(eval(x['recipes']))), axis=1).stack().reset_index(level=1, drop=True)
s.name = 'recipe'
cc = c.join(s)[['recipe', 'time']]
cc['package'] = cc.recipe.apply(lambda x: x.split('/')[0])
e = cc.groupby('package')['time'].agg('min')
df = d.set_index('package')
df['time'] = pd.to_datetime(e)
df['time'] -= pd.Timestamp(datetime.datetime.now())
df['days'] = df.dropna().time.apply(lambda x: -x.days)
df['log10(downloads)'] = np.log10(df['downloads'] + 1)


def callback(event):
    print(df.iloc[event.ind])


fig = plt.figure()
ax = fig.add_subplot(111)

# note we have to dropna ahead of time so that when interactively picking
# points, the event ind matches the df ind
sns.regplot('days', 'log10(downloads)', df.dropna(), ax=ax, scatter_kws=dict(picker=5))

if outfile:
    plt.savefig(outfile)
else:
    plt.gcf().canvas.mpl_connect('pick_event', callback)
    plt.show()
