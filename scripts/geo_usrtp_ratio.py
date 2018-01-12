#%%
import BikeSystem
from IPython.display import display
import matplotlib.pyplot as plt
bs = BikeSystem.ChicagoBikeSystem()
df = bs.load_data()
mp = bs.load_map()
#%%
data = []
for usertype in ["Casual", "Registered"]:
    df_ustp = df[df.usertype == usertype]
    counts = df_ustp.startstation.value_counts() + df_ustp.endstation.value_counts()
    # counts /= counts.max()
    data.append(counts)
ratio = data[1] / (data[1] + data[0])
ratio.describe()
#%%
import matplotlib
import numpy as np
norm = matplotlib.colors.Normalize(vmin=0, vmax=1, clip=True)
mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=matplotlib.cm.seismic_r)
def getColor(val):
    return tuple([int(i*255) for i in mapper.to_rgba(val)[:3]])
#%%
import gmaps
gmaps.configure(api_key='AIzaSyCkVUk-IJZvr6Fql6NMNli64S5GFzaRgb0')
locations = [bs.locate(st) for st in mp.index]
colors = [getColor(ratio[st]) for st in mp.index]
counts = df_ustp.startstation.value_counts() + df_ustp.endstation.value_counts()
weights = [int(counts[st]) + 1 for st in mp.index]
fig = gmaps.figure()
layer = gmaps.symbol_layer(locations, fill_color=colors, stroke_color=colors, scale=weights)
fig.add_layer(layer)
fig