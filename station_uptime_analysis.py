#%%
import BikeSystem
from IPython.display import display
import pandas as pd
bs = BikeSystem.ChicagoBikeSystem()
df = bs.load_data()
earliest = df.groupby("startstation")["starttime"].min()
earliest.rename(index={0: 'station'}, inplace=True)
latest = df.groupby("endstation")["stoptime"].max()
latest.rename(index={0: 'station'}, inplace=True)
timespan = pd.concat([earliest, latest], axis=1)
timespan["uptime"] = timespan.stoptime - timespan.starttime
timespan["updays"] = timespan.uptime.dt.days + 1
timespan