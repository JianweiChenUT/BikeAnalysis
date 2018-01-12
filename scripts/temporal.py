#%%
import BikeSystem
from IPython.display import display
import matplotlib.pyplot as plt
bs = BikeSystem.ChicagoBikeSystem()
df = bs.load_data()
mp = bs.load_map()
#%%
df["ID"] = df.index
df["hour"] = df.starttime.dt.hour
df
#%%
df.columns
#%%
start = df.groupby(["startstation", "hour", "usertype"]).count()["ID"]
stop = df.groupby(["endstation", "hour", "usertype"]).count()["ID"]
stop.index.rename(["station", "hour", "usertype"], inplace=True)
start.index.rename(["station", "hour", "usertype"], inplace=True)
start.fillna(0, inplace=True)
stop.fillna(0, inplace=True)
accu = start + stop
start = start.reset_index()
stop = stop.reset_index()
accu = accu.reset_index()
start.rename(columns={"ID": "count"}, inplace=True)
stop.rename(columns={"ID": "count"}, inplace=True)
accu.rename(columns={"ID": "count"}, inplace=True)
#%%
# Plot pattterns by usertype
from os import path
stations = list(mp.index)
for station in stations:
    st_data = accu[accu.station == station]
    print("Plotting {}...".format(station))
    for usertype in ["Casual", "Registered"]:
        title = "{}-{}".format(station, usertype)
        st_data_ustp = st_data[st_data.usertype == usertype]
        st_data_ustp.plot.bar(x = "hour", y = "count", color="#00bfff", alpha=0.8,
            title=title)
        plt.xlabel("Hour")
        plt.ylabel("Count")
        plt.savefig(path.join("figs_Chicago", title + ".pdf"))
        