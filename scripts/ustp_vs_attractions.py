#%%
# load usertype ratio data
import BikeSystem
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
from os import path
bs = BikeSystem.ChicagoBikeSystem()
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
#%%
# replace some station names
bs.data.startstation.replace(
    'Aberdeen St & Monroe St (Madison St)',
    'Aberdeen St & Monroe St',
    inplace=True)
bs.data.endstation.replace(
    'Aberdeen St & Monroe St (Madison St)',
    'Aberdeen St & Monroe St',
    inplace=True)
bs.dump_data()
#%%
# load attraction data
attraction = pd.read_csv(
    path.join('attractions', bs.city + ".csv"), index_col=0)
attraction.set_index('Name', inplace=True)
#%%
attractions = attraction.index
stations = mp.index
display(attractions)
display(stations)
latlngs = {
    x: tuple(
        attraction[attraction.index == x][["Latitude",
                                           "Longitude"]].as_matrix().flatten())
    for x in attractions
}
ratings = {
    x: float(attraction[attraction.index == x].Rating)
    for x in attractions
}
reviews = {
    x: float(attraction[attraction.index == x].Reviews)
    for x in attractions
}
#%%
from geopy.distance import vincenty


def distance(station, place):
    """ distance between station and place of interest"""
    st_latlng = tuple(bs.locate(station))
    return vincenty(st_latlng, latlngs[place]).miles


#%%
# linear regression
def expr(station, top=5, expo=1):
    val = 0
    attrs = list(attractions)
    attrs.sort(key=lambda x: distance(station, x))
    for j in attrs[:top]:
        val += 1 / distance(station, j) ** expo
    return val


import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
k, e = 3, 1.5
Y = ratio.as_matrix()
X = [expr(x, k, e) for x in ratio.index]
results = sm.OLS(Y, sm.add_constant(X)).fit()
print(k, e, results.rsquared)
