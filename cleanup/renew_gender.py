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
for bs in bss:
    df = bs.load_data()
    df.gender.replace(0, "Unknown", inplace=True)
    df.gender.replace(1, "Male", inplace=True)
    df.gender.replace(2, "Female", inplace=True)
    df.gender = df.gender.astype("category")
    bs.data = df
    bs.dump_data()