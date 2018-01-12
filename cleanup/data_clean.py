#%%
%load_ext autoreload
%autoreload 2
#%%
from IPython.display import display
import BikeSystem
bss = [
    BikeSystem.BostonBikeSystem(),
    BikeSystem.ChicagoBikeSystem(),
    BikeSystem.NewYorkBikeSystem(),
    BikeSystem.DCBikeSystem()
]
#%%
# clean up map files for entries like "\n" or 0.0 in coordinates
import numpy as np
for bs in bss:
    mp = bs.load_map()
    if "Station" in bs.mp:
        bs.mp.set_index("Station", inplace=True)
        bs.dump_map()
    mp = mp[(mp["Latitude"].apply(np.isreal) & mp["Longitude"].apply(np.isreal))]
    mp["Latitutde"] = mp["Latitude"].astype(float)
    mp["Longitude"] = mp["Longitude"].astype(float)
    mp = mp[(~mp.Latitude.apply(lambda x: np.abs(x) < 1e-5)) & (~mp.Longitude.apply(lambda x: np.abs(x) < 1e-5))]
    bs.mp = mp
    bs.dump_map()
#%%
import BikeSystem
# statistic of how many stations can be geocoded
for bs in bss:
    %time bs.load_data()
    bs.load_map()
    geocodable = bs.data[bs.data.startstation.isin(bs.mp.index)
                        & bs.data.endstation.isin(bs.mp.index)]
    print("{} out of {} can be geocoded. ({:.4%})".format(len(geocodable), len(bs.data), len(geocodable) / len(bs.data)))
    
#%%
# merge duplicate stations
for bs in bss:
    %time bs.load_data()
    bs.load_map()
    all_stations = bs.all_stations
    print("{} stations referenced in data file.".format(len(all_stations)))
    geocodable_stations = all_stations.intersection(bs.mp.index)
    print("{} stations are geocodable".format(len(geocodable_stations)))
    stations = list(geocodable_stations)
    n = len(stations)
    for i, sa in enumerate(stations):
        ca = bs.locate(sa)
        dups = []
        for j, sb in enumerate(stations[i + 1:]):
            cb = bs.locate(sb)
            if np.linalg.norm(ca - cb) < 1e-4:
                dups.append((sb, cb))
        if len(dups) > 0:
            print("Duplicates for [{}] ({}):".format(sa, ca))
            for sb, cb in dups:
                print("\t[{}]({})".format(sb, cb))
            bs.data.startstation.replace(sb, sa, inplace=True)
            bs.data.endstation.replace(sb, sa, inplace=True)
    bs.dump_data()

#%%
# remove unreferenced index in map
for bs in bss:
    %time bs.load_data()
    bs.load_map()
    all_stations = bs.all_stations
    mp_stations = set(bs.mp.index)
    unreferenced = mp_stations.difference(all_stations)
    print("Dropping {} stations from mp:".format(len(unreferenced)))
    # for i in unreferenced:
    #     print("\t", i)
    bs.mp.drop(unreferenced, inplace=True)
    bs.dump_map()

#%% 
# check datatypes of data files
for bs in bss:
    %time bs.load_data()
    for col in bs.data.columns:
        print(col, bs.data[col].dtype)
    display(bs.data.memory_usage(deep=True))
    print('converting ["startstation", "endstations", "usertype"]...')
    for col in ["startstation", "endstation", "usertype"]:
        bs.data[col] = bs.data[col].astype("category")
    display(bs.data.memory_usage(deep=True))
    print('converting ["birthyear", "gender"]...')
    for col in ["birthyear", "gender"]:
        bs.data[col] = bs.data[col].astype("category")
    display(bs.data.memory_usage(deep=True))
    display(bs.data.head())
    bs.dump_data()