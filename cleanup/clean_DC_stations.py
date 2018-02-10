#%%
import BikeSystem
import re
from IPython.display import display
pattern = re.compile(r'\(\d+\)')
bs = BikeSystem.DCBikeSystem()
bs.load_map()
bs.load_data()
stations = list(bs.mp.index)
replace = {}
cnt = 0
for st in stations:
    if len(pattern.findall(st)) > 0:
        rep = pattern.sub("", st).strip()
        if rep in bs.mp.index:
            replace[st] = rep
        else:
            cnt += 1
orig = (list(replace.keys()))
aft = (list(replace.values()))
bs.data.startstation.replace(orig, aft, inplace=True)
bs.data.endstation.replace(orig, aft, inplace=True)
print("Count = ", cnt)
list(sorted(bs.data.startstation.unique()))
#%%
bs.dump_data()