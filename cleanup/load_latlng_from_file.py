#%%
import sys
import BikeSystem
import timeit
import subprocess
import os
import CSVLoader
import pandas as pd
from collections import defaultdict
bs = BikeSystem.NewYorkBikeSystem()
default_map = bs.load_map()
complete_map = pd.DataFrame()
files = bs.get_files()
#%%
for f in files:
    print("Loading %s..." % f)
    start = timeit.default_timer()
    df = pd.read_csv(f)
    end = timeit.default_timer()
    print("Loading used: ", end - start)
    start = end
    df.rename(columns={c: c.lower() for c in df.columns}, inplace=True)
    try:
        df1 = df[[
            "start station name",
            "start station latitude",
            "start station longitude",
        ]].copy()
    except KeyError:
        continue
    df1.rename(columns={c: c[6:] for c in df1.columns}, inplace=True)
    df1.drop_duplicates(inplace=True)
    df2 = df[[
        "end station name",
        "end station latitude",
        "end station longitude",
    ]].copy()
    df2.rename(columns={c: c[4:] for c in df2.columns}, inplace=True)
    df2.drop_duplicates(inplace=True)
    complete_map = complete_map.append(df1).append(df2)
    complete_map.drop_duplicates(inplace=True)
    completed_map = complete_map.reset_index(drop=True)
    end = timeit.default_timer()
    del df, df1, df2
    print("Process used: ", end - start)
#%%
complete_map.sort_values('station name', inplace=True)
complete_map.drop_duplicates(inplace=True)
complete_map.reset_index(drop=True, inplace=True)
complete_map["Docks"] = 0
complete_map.rename(
    columns={
        "station name": "Station",
        "station latitude": "Latitude",
        "station longitude": "Longitude",
        "Lattitude": "Latitude"
    },
    inplace=True)
complete_map["Municipality"] = "New York"
complete_map
#%%
exist_stations = set(default_map.Station)
# default_map.reset_index(inplace=True, drop=True)
# exist_stations
default_map
#%%
for i, row in complete_map.iterrows():
    if row["Station"] in exist_stations:
        continue
    print("inserting ", (row["Station"]))
    default_map = default_map.append(row)
default_map.sort_values("Station", inplace=True)
default_map.reset_index(inplace=True, drop=True)
default_map

#%%
from IPython.display import display
exist_stations = set(default_map["Station"])
for st in exist_stations:
    samename = default_map[default_map.Station == st]
    if len(samename) > 1:
        display(samename)
#%%
default_map.reset_index(inplace=True, drop=True)
default_map.set_index("Station", inplace=True)
#%%
bs.mp = default_map
bs.dump_map()