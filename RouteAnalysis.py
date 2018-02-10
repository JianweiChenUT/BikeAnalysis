#%%
import os
import BikeSystem
import pandas as pd
import numpy as np
from IPython.display import display
from collections import defaultdict
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from shutil import rmtree, copyfile
import time
import gmaps
gmaps.configure(api_key='AIzaSyCkVUk-IJZvr6Fql6NMNli64S5GFzaRgb0')


def fname(name):
    return name.replace("/", "or")


class RouteAnalysis:
    def __init__(self, bs):
        self.bikesystem = bs
        self.df = bs.load_data()
        self.mp = bs.load_map()
        self.df["hour"] = self.df.starttime.dt.hour
        self.route_dis = self.route_distribution()
        self.routes = defaultdict(int)
        for i, j in self.route_dis.iterrows():
            if i[0] != i[1]:
                self.routes[tuple(sorted(i))] += int(j)

    def route_distribution(self):
        grpby = self.df.groupby(["startstation", "endstation"])
        hour_count = grpby["hour"].count().to_frame()
        return hour_count

    def highfreq_routes(self, freq):
        return {i: j for i, j in self.routes.items() if j > freq}

    def plot_route(self, key, base_dir=None, save=True):
        print("Plotting ", key)
        loc_a, loc_b = key
        df = self.bikesystem.data
        flow_a = df[(df.startstation == loc_a)
                    & (df.endstation == loc_b)].hour.value_counts()
        flow_b = df[(df.startstation == loc_b)
                    & (df.endstation == loc_a)].hour.value_counts()
        x = np.arange(0, 24, dtype=int)
        y1 = [flow_a.get(i, 0) for i in x]
        y2 = [flow_b.get(i, 0) for i in x]
        plt.clf()
        plt.bar(x, y1, color='red', alpha=0.6, width=0.3)
        plt.bar(x + 0.3, y2, color='blue', alpha=0.6, width=0.3)
        title = " - ".join(key)
        plt.title(title)
        plt.xlabel("Hour")
        if save:
            plt.savefig(os.path.join(base_dir, fname(title) + ".pdf"))
        else:
            plt.show()

    def plot_routes(self, freq=500):
        base_dir = self.bikesystem.city + "_Route"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for i in self.highfreq_routes(freq):
            self.plot_route(i, base_dir)

    def plot_route_map(self, freq):
        station_pairs = [sorted(i) for i in (self.route_dis.index)]
        bs = self.bikesystem
        fig = gmaps.figure(
            center=tuple(bs.locate(bs.mp.index[0])), zoom_level=11)
        layer = gmaps.drawing_layer(features=[
            gmaps.Line(start=tuple(bs.locate(i)), end=tuple(bs.locate(j)))
            for i, j in self.highfreq_routes(freq)
        ])
        fig.add_layer(layer)
        return fig

    def cluster(self, res, n_cluster, **kwargs):
        series, names = [], []
        df = self.bikesystem.data
        with np.errstate(divide='ignore'):
            for (loc_a, loc_b) in res:
                flow_a = df[(df.startstation == loc_a)
                            & (df.endstation == loc_b)].hour.value_counts()
                flow_b = df[(df.startstation == loc_b)
                            & (df.endstation == loc_a)].hour.value_counts()
                x = np.arange(5, 24, dtype=int)
                y1 = np.array([flow_a.get(i, 0) for i in x])
                y2 = np.array([flow_b.get(i, 0) for i in x])
                a, b = np.minimum(y1, y2), np.maximum(y1, y2)
                res = (b - a) / b
                res[b == 0] = 0
                series.append(res)
                names.append((loc_a, loc_b))

        km = KMeans(init='k-means++', n_clusters=n_cluster)
        labels = km.fit_predict(np.array(series))
        base_dir = os.path.join('route_clusters', self.bikesystem.city + "_{}".format(n_cluster))
        if os.path.exists(base_dir):
            rmtree(base_dir)
        from_dir = os.path.join('Route', '{}_Route'.format(
            self.bikesystem.city))
        for i in range(n_cluster):
            path_name = os.path.join(base_dir, str(i))
            os.makedirs(path_name)
        for name, label in zip(names, labels):
            file_name = fname(" - ".join(name)) + ".pdf"
            copyfile(
                os.path.join(from_dir, file_name),
                os.path.join(base_dir, str(label), file_name))
        return names, labels
