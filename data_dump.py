#%%
import BikeSystem
import pandas as pd
#%%
bs = BikeSystem.DCBikeSystem()
df = bs.load_data()
df.columns
# mp = bs.load_map()
# mp.to_csv("export/{}_Geocoding.csv".format(bs.city))
# cnt_1 = df.startstation.value_counts()
# cnt_2 = df.endstation.value_counts()
# start = df.groupby("startstation")["starttime"].min()
# end = df.groupby("endstation")["stoptime"].max()
# res = pd.DataFrame({
#     "Checkout_Count": cnt_1,
#     "ReturnCount": cnt_2,
#     "EarliestRecord": start,
#     "LatestRecord": end
# })
# res.to_csv("export/{}_Activity.csv".format(bs.city))
