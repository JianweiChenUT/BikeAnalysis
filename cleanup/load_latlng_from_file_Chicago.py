#%%
%load_ext autoreload
%autoreload 2
#%%
import sys
import BikeSystem
import timeit
import subprocess
import os
import CSVLoader
import pandas as pd
from collections import defaultdict
from IPython.display import display
bs = BikeSystem.ChicagoBikeSystem()
default_map = bs.load_map()
complete_map = pd.DataFrame()
files = bs.get_files()
def get_files(dir_name):
    files = []
    for sub in os.listdir(dir_name):
        sub_dir = os.path.join(dir_name, sub)
        if os.path.isdir(sub_dir):
            files.extend(get_files(sub_dir))
            continue
        if sub.endswith(".zip"):
            continue
        if "station" in sub.lower():
            files.append(sub_dir)
    return files
print(len(default_map))
#%%
complete_map = pd.DataFrame()
for f in get_files(bs.raw_dir):
    if f.endswith(".csv"):
        df = pd.read_csv(f)
    else:
        df = pd.read_excel(f)
    complete_map = complete_map.append(df)
col_mapping = {
    "latitude": "Latitude",
    "longitude": "Longitude",
    "name": "Station",
    "dpcapacity": "Docks",
    # "online date": "online_date"
}
complete_map.rename(columns=col_mapping, inplace=True)
complete_map = complete_map[["Station", "Latitude", "Longitude", "Docks"]].copy()
complete_map["Municipality"] = "Chicago"
complete_map.drop_duplicates(inplace=True)
complete_map.reset_index(drop=True, inplace=True)
complete_map.sort_values(["Station", "Docks"], inplace=True)
complete_map
#%%
default_map["Mark"] = True
default_map = default_map.append(complete_map)
default_map.sort_values(["Station", "Mark"], inplace=True)
default_map.drop_duplicates(["Station"], inplace=True, keep="first")
exist_stations = set(default_map["Station"])
for st in exist_stations:
    samename = default_map[default_map.Station == st]
    if len(samename) > 1:
        display(samename)
#%%
default_map.reset_index(inplace=True, drop=True)
del default_map["Mark"]
bs.mp = default_map
bs.dump_map()