#%%
import BikeSystem
bs = BikeSystem.ChicagoBikeSystem()
bs.load_data()
bs.load_map()
replace = {
    'Aberdeen St & Monroe St (Madison St)': 'Aberdeen St & Monroe St',
    'Green St (Halsted St) & Madison St': 'Green St & Madison St',
    'Paulina  Ave (Wood St) & North Ave': 'Paulina Ave & North Ave',
    'Wabash Ave (State St) & 16th St': 'Wabash Ave & 16th St',
    'Wells St & Concord Pl': 'Wells St & Concord Ln'
}
bs.data.startstation.replace(
    list(replace.keys()), list(replace.values()), inplace=True)
bs.data.endstation.replace(
    list(replace.keys()), list(replace.values()), inplace=True)
#%%
s = set(bs.mp.index)
start = set(bs.data.startstation)
print(start.difference(s))
end = set(bs.data.endstation)
print(end.difference(s))
bs.mp
#%%
if "Latitutde" in bs.mp:
    del bs.mp["Latitutde"]
bs.mp.loc["Clinton St & Jackson Blvd"] = [
    0, 41.8780339, -87.6432437, "Chicago"
]
bs.mp
#%%
bs.dump_map()
bs.dump_data()