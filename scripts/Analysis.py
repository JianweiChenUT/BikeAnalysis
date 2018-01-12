#%%
%load_ext autoreload
%autoreload 2
#%%
import BikeSystem
import gmaps
gmaps.configure(api_key='AIzaSyDrkUKw9ulVuMuVhyqAx8xQX-5DIxErG2k')
#%%
bs = BikeSystem.ChicagoBikeSystem()
mp = bs.load_map()
data = bs.load_data()
#%%
print("The trip data ranges from {} to {}.".format(data.starttime.min(), data.stoptime.max()))
%time data["Year"] = data.starttime.dt.year
#%%
import matplotlib.pyplot as plt
data.groupby("Year").count()["starttime"].plot(x="Year", y="starttime", kind="bar", 
    title="Activity Distribution by Year({})".format(bs.city))
plt.show()
#%%
data["Month"] = data.starttime.dt.month
for year in range(2013, 2018):
    data[data.Year == year].groupby("Month").count()["starttime"].plot(x = "Month", 
        y = "starttime", kind="bar", color="blue", alpha=0.6,
        title="Activity Distribution by Month({}, {})".format(bs.city, year))
    plt.show()
#%%
data["Weekday"] =data.starttime.dt.weekday
data.groupby("Weekday").count()["starttime"].plot(x = "Weekday", 
    y = "starttime", kind="bar", color="blue", alpha=0.6,
    title="Activity Distribution by Weekday({})".format(bs.city))
plt.show()
#%%
data.usertype.value_counts().plot(kind='pie', figsize=(6, 6), legend = True,
    title="Distribution of Registered / Casual Trips",)
plt.show()
for usertp in data.usertype.unique():
    subdata = data[(data.Year > 2013) & (data.Year < 2017) & (data.usertype == usertp)]
    subdata.groupby("Month").count()["starttime"].plot(x = "Month", 
        y = "starttime", kind="bar", color="blue", alpha=0.6,
        title="Activity Distribution by Month (Aggregated 2014-2016)({}, {})".format(bs.city, usertp))
    plt.show()

for usertp in data.usertype.unique():
    data[data.usertype == usertp].groupby("Weekday").count()["starttime"].plot(x = "Weekday", 
        y = "starttime", kind="bar", color="blue", alpha=0.6,
        title="Activity Distribution by Weekday({}, {})".format(bs.city, usertp))
    plt.show()
#%%
station_latlngs = [bs.locate(st) for st in bs.mp.index]
fig = gmaps.figure()
markers = gmaps.marker_layer(station_latlngs)
fig.add_layer(markers)
fig
