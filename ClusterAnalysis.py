#%%
import BikeSystem
import pandas as pd
import os
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from matplotlib.pyplot import cm
from shutil import copyfile, rmtree
from dtw import fastdtw
import numpy as np
from matplotlib.colors import rgb2hex
from matplotlib.pyplot import cm
import gmaps
gmaps.configure(api_key='AIzaSyCkVUk-IJZvr6Fql6NMNli64S5GFzaRgb0')


def fname(s):
    return s.replace("/", " or ")


def simOfSet(s1, s2, similarity, linkage="average"):
    if linkage == "average":
        return np.average([similarity[i, j] for i in s1 for j in s2])
    elif linkage == "single":
        return np.max([similarity[i, j] for i in s1 for j in s2])
    elif linkage == "complete":
        return np.min([similarity[i, j] for i in s1 for j in s2])


def agg_cluster(similarity, n_cluster, linkage="average"):
    n = len(similarity)
    sets = [set([i]) for i in range(n)]
    while (len(sets) > n_cluster):
        nset = len(sets)
        min_dist = simOfSet(sets[0], sets[1], similarity, linkage=linkage)
        pair = (0, 1)
        for i in range(nset):
            for j in range(i + 1, nset):
                val = simOfSet(sets[i], sets[j], similarity, linkage=linkage)
                if val < min_dist:
                    min_dist = val
                    pair = (i, j)
        i, j = pair
        sets[i].update(sets[j])
        del sets[j]
    labels = np.arange(n)
    for label, s in enumerate(sets):
        for i in s:
            labels[i] = label
    return labels


#%%
class ClusterAnalysis:
    def __init__(self, bikesystem):
        self.bikesystem = bikesystem
        bikesystem.load_map()
        bikesystem.load_data()

    def timespan(self):
        df = self.bikesystem.data
        earliest = df.groupby("startstation")["starttime"].min()
        earliest.rename(index={0: 'station'}, inplace=True)
        latest = df.groupby("endstation")["stoptime"].max()
        latest.rename(index={0: 'station'}, inplace=True)
        timespan = pd.concat([earliest, latest], axis=1)
        timespan[
            "updays"] = (timespan.stoptime - timespan.starttime).dt.days + 1
        timespan = timespan.updays.to_frame()
        timespan.rename(index={0: 'station'}, inplace=True)
        return timespan

    def preprocess(self):
        df = self.bikesystem.data
        df["Hour"] = df.starttime.dt.hour
        start = df.groupby(["startstation", "Hour"])["starttime"].count()
        end = df.groupby(["endstation", "Hour"])["starttime"].count()
        start.index.rename('station', level=0, inplace=True)
        start.rename("Checkout", inplace=True)
        end.index.rename('station', level=0, inplace=True)
        end.rename("Return", inplace=True)
        res = pd.concat([start, end], axis=1)
        res.fillna(0, inplace=True)
        timespan = self.timespan()
        res["Factor"] = res.apply(
            lambda x: timespan.at[x.name[0], 'updays'], axis=1)
        res["Checkout"] /= res["Factor"]
        res["Return"] /= res["Factor"]
        res["Delta"] = res.Return - res.Checkout
        return res

    def clean_record(self, data):
        hours = set(range(0, 24))
        missing = list(hours.difference(data.index))
        tmp_df = pd.DataFrame(
            data=np.zeros((len(missing), 4)),
            index=missing,
            columns=data.columns)
        tmp_df.Factor = data.Factor.iloc[0]
        data = pd.concat([data, tmp_df])
        data.sort_index(inplace=True)
        return data

    def cluster(self,
                res,
                n_cluster,
                by_feature,
                method='kmeans',
                normalized=False,
                **kwargs):
        stations = list(set(res.index.get_level_values(0)))
        series, names = [], []
                
        def transform(x):
            return x / np.max(np.abs(x)) if normalized else x

        def feature(data):
            if by_feature == "Combined":
                return data[["Checkout", "Return"]].values.flatten()
            else:
                return data[by_feature]

        for st in stations:
            data = res.loc[st]
            if len(data) < 24:
                data = self.clean_record(data)
            if res.loc[st].Factor.iloc[0] < 30 or np.isnan(feature(data)).any()\
                or (feature(data) == 0).all():
                continue
            series.append(transform(feature(data)))
            names.append(st)
        if method == 'kmeans':
            km = KMeans(init='k-means++', n_clusters=n_cluster)
            labels = km.fit_predict(np.array(series))
        elif method == 'agglomerative':
            n = len(series)
            simmat = np.zeros((n, n))
            for i in range(n):
                simmat[i, i] = 0
                for j in range(i + 1, n):
                    simmat[i, j], _, _, _ = fastdtw(
                        series[i], series[j], dist=lambda x, y: np.abs(x - y))
                    simmat[j, i] = simmat[i, j]
            labels = agg_cluster(
                simmat, n_cluster, linkage=kwargs.get('linkage', 'average'))
        path_name = '{}_{}_{}'.format(method, self.bikesystem.city, n_cluster)
        path_name = path_name + "_normalized" if normalized else path_name
        base_dir = os.path.join('clusters', path_name)
        if os.path.exists(base_dir):
            rmtree(base_dir)
        from_dir = os.path.join('temporal_deltas', '{}_Hourly'.format(
            self.bikesystem.city))
        for i in range(n_cluster):
            path_name = os.path.join(base_dir, str(i))
            os.makedirs(path_name)
        for name, label in zip(names, labels):
            file_name = fname(name) + ".pdf"
            copyfile(
                os.path.join(from_dir, file_name),
                os.path.join(base_dir, str(label), file_name))
        return names, labels

    def plot_clusters(self, cluster_res, n_cluster):
        names, labels = cluster_res
        locations = [tuple(self.bikesystem.locate(i)) for i in names]
        colormap = [rgb2hex(i[:3]) for i in cm.rainbow(np.linspace(0, 1, n_cluster))]
        colors = [colormap[i] for i in labels]
        fig = gmaps.figure()
        layer = gmaps.symbol_layer(
            locations, fill_color=colors, stroke_color=colors)
        fig.add_layer(layer)
        return fig, colormap

    def plot_complete(self, res):
        plt.clf()
        plt.figure(figsize=(20, 20))
        width, opacity = 0.35, 0.4
        index = np.arange(0, 24)
        ax = plt.gca()
        ax.spines['left'].set_position(('axes', 0))
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        stations = set(res.index.get_level_values(0))
        for st in stations:
            data = res.loc[st]
            if len(data) < 24:
                data = self.clean_record(data)
            ax.plot(index, data.Delta, '-o', 'c', label='return-checkout')
        ax.xaxis.set_label_coords(0.5, 0)
        plt.title(self.bikesystem.city)
        plt.xlabel('Time of Day (Hour)')
        plt.ylabel('Normalized Activity')
        plt.savefig(
            os.path.join('city_hourly', self.bikesystem.city + "_Hourly.pdf"))

    def hourlyPlot(self, res, delta_only=True):
        if delta_only:
            basedir = os.path.join('temporal_deltas',
                                   self.bikesystem.city + "_Hourly")
        else:
            basedir = os.path.join('temporal_patterns',
                                   self.bikesystem.city + "_Hourly")
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        stations = set(res.index.get_level_values(0))
        for st in stations:
            data = res.loc[st]
            if len(data) < 24:
                data = self.clean_record(data)
            plt.clf()
            plt.figure(figsize=(8, 6))
            width, opacity = 0.35, 0.4
            index = np.arange(0, 24)
            ax = plt.gca()
            ax.spines['left'].set_position(('axes', 0))
            ax.spines['right'].set_color('none')
            ax.spines['bottom'].set_position('zero')
            ax.spines['top'].set_color('none')
            ax.spines['left'].set_smart_bounds(True)
            ax.spines['bottom'].set_smart_bounds(True)
            ax.plot(index, data.Delta, '-o', 'c', label='return-checkout')
            if not delta_only:
                rect1 = ax.bar(
                    index,
                    data.Return,
                    width,
                    alpha=opacity,
                    color='b',
                    label='return')
                rect2 = ax.bar(
                    index + width,
                    data.Checkout,
                    width,
                    alpha=opacity,
                    color='r',
                    label='checkout')
                ax.legend()
            ax.xaxis.set_label_coords(0.5, 0)
            plt.title(st)
            plt.xlabel('Time of Day (Hour)')
            plt.ylabel('Normalized Activity')
            file_path = os.path.join(basedir, fname(st) + ".pdf")
            plt.savefig(file_path)
            print("Saved {}".format(file_path))


# bs = BikeSystem.BostonBikeSystem()
# cl = ClusterAnalysis(bs)
# res = cl.preprocess()
# cluster_res = cl.cluster(res, 8, method='kmeans', normalized=True)