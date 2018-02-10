#%%
import BikeSystem
from IPython.display import display
bs = BikeSystem.DCBikeSystem()
bs.load_data()
bs.load_map()
replace = { }
bs.data.startstation.replace(
    list(replace.keys()), list(replace.values()), inplace=True)
bs.data.endstation.replace(
    list(replace.keys()), list(replace.values()), inplace=True)
#%%
(bs.mp[bs.mp.index.str.startswith('A')])
#%%
s = set(bs.mp.index)
start = set(bs.data.startstation)
display(start.difference(s))
end = set(bs.data.endstation)
display(end.difference(s))
#%%
if "Latitutde" in bs.mp:
    del bs.mp["Latitutde"]
bs.mp.loc["JFK / UMASS Station"] = [42.3206058, -71.0545533, 'Boston', 0]
bs.mp.loc["JP Monument - South St at Centre St"] = [
    42.3092925, -71.1177815, 'Boston', 0
]
bs.mp.loc["Longwood Ave/Riverway"] = [42.3399202, -71.1102082, 'Boston', 0]
bs.mp.loc["Harvard Real Estate - North Harvard St at Western Ave"] = [
    42.3631872, -71.1319815, 'Boston', 0
]
bs.mp.loc["Harvard University River Houses - DeWolfe St at Grant St"] = [
    42.3699013, -71.1190082, 'Boston', 0
]
bs.mp.loc["Milk St at India St"] = [42.3584383, -71.0539795, 'Boston', 0]
bs.mp.loc["Overland St at Brookline Ave"] = [
    42.3460602, -71.1019242, 'Boston', 0
]
bs.mp.loc["South Bay Plaza"] = [42.3277713, -71.0653531, 'Boston', 0]
#%%
bs.dump_map()
bs.dump_data()