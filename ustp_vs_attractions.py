#%%
# load usertype ratio data
import BikeSystem
from IPython.display import display
from geopy.distance import vincenty
import matplotlib.pyplot as plt
import pandas as pd
from os import path
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import gmaps
from ipywidgets.embed import embed_minimal_html
gmaps.configure(api_key='AIzaSyCkVUk-IJZvr6Fql6NMNli64S5GFzaRgb0')
bs = BikeSystem.NewYorkBikeSystem()
df = bs.load_data()
mp = bs.load_map()
data = []
for usertype in ["Casual", "Registered"]:
    df_ustp = df[df.usertype == usertype]
    counts = df_ustp.startstation.value_counts(
    ) + df_ustp.endstation.value_counts()
    data.append(counts)
ratio = data[0] / (data[1] + data[0])
ratio = ratio[(~ratio.isna()) & ratio.index.isin(mp.index)]
ratio.describe()
#%%
# load attraction data
attraction = pd.read_csv(
    path.join('attractions', bs.city + ".csv"), index_col=0)
attraction.set_index('Name', inplace=True)
attractions = attraction.index
stations = mp.index
latlngs = {
    x: tuple([attraction.at[x, 'Latitude'], attraction.at[x, 'Longitude']])
    for x in attractions
}
ratings = {x: attraction.at[x, 'Rating'] for x in attractions}
reviews = {x: attraction.at[x, 'Reviews'] for x in attractions}
ratio.sort_values(inplace=True, ascending=False)
#%%


def distance(station, place):
    """ distance between station and place of interest"""
    try:
        st_latlng = tuple(bs.locate(station))
        return vincenty(st_latlng, latlngs[place]).miles
    except Exception:
        print(station, place, st_latlng, latlngs[place])

def parse_result(result, tags):
    summ = str(results.summary())
    data = [i.split() for i in summ.split('\n') if i.startswith('x')]
    res = []
    for tag, line in zip(tags, data):
        if float(line[4]) < 0.05:
            res.append([tag, line[1], line[4]])
    return res

def top_K_closest(station, k=5):
    lst = [(distance(station, j), j) for j in attractions]
    mask = set([st for dis, st in sorted(lst, reverse=False)[:k]])
    return [1. / dis if st in mask else 0 for dis, st in lst]
        
def plot_clusters(res):
    locations = [tuple(bs.locate(i)) for i, _, _ in res]
    colors = ['red' if float(coef) > 0 else 'blue' for _, coef, _ in res]
    fig = gmaps.figure()
    layer = gmaps.symbol_layer(
        locations, fill_color=colors, stroke_color=colors)
    fig.add_layer(layer)
    top_ratios = ratio[:len(locations)]
    locations = [tuple(bs.locate(i)) for i in top_ratios.index]
    layer = gmaps.symbol_layer(
        locations, fill_color='black', stroke_color='black')
    fig.add_layer(layer)
    return fig


Y = ratio.as_matrix()
X = np.array([top_K_closest(x, k=50) for x in ratio.index])
results = sm.OLS(Y, sm.add_constant(X)).fit()
res = parse_result(results, ratio.index)
fig = plot_clusters(res)
embed_minimal_html('{}.html'.format(bs.city), views=[fig])
res