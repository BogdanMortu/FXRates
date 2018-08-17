import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as pt
import numpy as np

conn = sqlite3.connect('rates.db')

# get the rates table into a dataframe
df = pd.read_sql_query("select * from rates;", conn)

# prepare the correct datatypes for the columns
# convert all the rates to float
df.loc[:, 'currency_official_rate':'currency_ask_rate'] = \
    df.loc[:, 'currency_official_rate':'currency_ask_rate'].applymap(float)

# split insert_time column between date and time
# df['date'] = df.insert_time.str.split('-').apply(lambda x: x[0]).str.strip()
# df['time'] = df.insert_time.str.split('-').apply(lambda x: x[1]).str.strip()

# convert insert_time column to datetime datatype
df['insert_time'] = df.insert_time.str.replace('-', '')
df['insert_time'] = pd.to_datetime(df['insert_time'], dayfirst=True, infer_datetime_format=True)

# add&compute 2 new columns (expressed in pips)
df['bid_spread'] = ((df['currency_official_rate'] - df['currency_bid_rate']) * 10000).apply(np.ceil).astype(int)
df['ask_spread'] = ((df['currency_ask_rate'] - df['currency_official_rate']) * 10000).apply(np.ceil).astype(int)

# add 2 new columns with categories for bid_spread&ask_spread
bins = [0, 300, 600, 900, 1200]
names = ['<300', '300-600', '600-900', '900+']

d = dict(enumerate(names, 1))

df['BidSpreadCategory'] = list(map(d.get, np.digitize(df['bid_spread'], bins)))
df['AskSpreadCategory'] = list(map(d.get, np.digitize(df['ask_spread'], bins)))

# set column type as 'category'
df['BidSpreadCategory'] = df['BidSpreadCategory'].astype('category')
df['AskSpreadCategory'] = df['AskSpreadCategory'].astype('category')

# change the index
df = df.set_index('insert_time')

# computing a figure with 2 graphics
pt.style.use('seaborn-dark-palette')
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

pt.rc('font', size=SMALL_SIZE)  # controls default text sizes
pt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
pt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
pt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
pt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
pt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
pt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

fig = pt.figure()
fig.patch.set_facecolor('#D8D8D8')

# figure - subplot 1
graph1 = fig.add_subplot(1, 2, 1, facecolor='#CEE3F6', alpha=0.8)
graph1.spines['top'].set_visible(False)
graph1.spines['right'].set_visible(False)
graph1.spines['left'].set_visible(False)
grouped = df.groupby('BidSpreadCategory')
for key, group in grouped:
    data = group.groupby(
        [lambda x: datetime.strptime(str(x.year), '%Y'), lambda x: datetime.strptime(str(x.month), '%m')]).count()
    data['BidSpreadCategory'].plot(label=key, linewidth=2.0)
graph1.set_title("Count of BidSpreads")

# figure - subplot 2
graph2 = fig.add_subplot(1, 2, 2, facecolor='#CEE3F6', alpha=0.8)
graph2.spines['top'].set_visible(False)
graph2.spines['right'].set_visible(False)
graph2.spines['left'].set_visible(False)
grouped = df.groupby('AskSpreadCategory')
for key, group in grouped:
    data = group.groupby([lambda x: datetime.strptime(str(x.year), '%Y')
                             , lambda x: datetime.strptime(str(x.month), '%m')]
                         ).count()
    data['AskSpreadCategory'].plot(label=key, linewidth=2.0)
graph2.set_title("Count of AskSpreads")

pt.autoscale(tight=True)
pt.legend()
pt.show()
