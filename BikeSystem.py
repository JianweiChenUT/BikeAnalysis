from os import path, listdir
from abc import ABC
import pandas as pd
import timeit
from CSVLoader import CSVLoader
DATA_DIR = path.join(path.dirname(__file__), 'data')
RAW_DIR = path.join(path.dirname(__file__), 'raw_data')


class BikeSystem(ABC):
    @property
    def dir_name(self):
        return path.join(DATA_DIR, getattr(self, 'city'))

    @property
    def raw_dir(self):
        return path.join(RAW_DIR, getattr(self, 'city'))

    @property
    def map_file(self):
        return path.join(self.dir_name, getattr(self, 'city') + "Map.pkl")

    @property
    def data_file(self):
        return path.join(self.dir_name, getattr(self, 'city') + ".pkl")

    @property
    def all_stations(self):
        stations = set(self.data.startstation.unique())
        stations.update(self.data.endstation.unique())
        return stations

    def load_data(self, persist=True):
        res = self._load_data(getattr(self, 'loader'))
        if persist:
            self.data = res
        print("Loaded {} rows from {}.".format(len(res), self.data_file))
        return res

    def locate(self, station):
        if getattr(self, '_cache', None) == None:
            self._cache = {
                i: row[["Latitude",
                                     "Longitude"]].as_matrix().flatten()
                for i, row in self.mp.iterrows()
            }
        return self._cache[station]

    def filter_geocodable(self):
        n = len(self.data)
        print("Before filtering ungeocodable nrows = ", len(self.data))
        stations = self.mp.index
        res = self.data[self.data.startstation.isin(stations)
                              & self.data.endstation.isin(stations)]
        print("After filtering nrows = ", len(self.data))
        print(len(self.data) / n, " remains.")
        return res

    def _load_data(self, loader):
        if path.exists(self.data_file):
            return pd.read_pickle(self.data_file)
        files = self.get_files()
        dfs = [loader(f) for f in files]
        df = pd.concat(dfs)
        category = [
            "startstation", "endstation", "usertype", "birthyear", "gender"
        ]
        for cat in category:
            df[cat] = df[cat].astype('category')
        df.to_pickle(self.data_file)
        return df

    def get_files(self):
        pass

    def load_map(self):
        self.mp = pd.read_pickle(self.map_file)
        print("Loaded {} bike stations from {}.".format(len(self.mp), self.city))
        return self.mp

    def dump_map(self):
        self.mp.to_pickle(self.map_file)

    def dump_data(self):
        self.data.to_pickle(self.data_file)


class ChicagoBikeSystem(BikeSystem):
    city = "Chicago"
    loader = CSVLoader.load_divvy

    def get_files(self):
        files = []
        for subdir in listdir(self.raw_dir):
            subdir_path = path.join(self.raw_dir, subdir)
            if not path.isdir(subdir_path):
                continue
            for file in listdir(subdir_path):
                if file.endswith(".csv") and "Trips" in file:
                    files.append(path.join(subdir_path, file))
        return files


class NewYorkBikeSystem(BikeSystem):
    city = "NewYork"
    loader = CSVLoader.load_citibike

    def get_files(self):
        return [
            path.join(self.raw_dir, f) for f in listdir(self.raw_dir)
            if f.endswith(".csv")
        ]


class BostonBikeSystem(BikeSystem):
    city = "Boston"
    loader = CSVLoader.load_hubway

    def get_files(self):
        files = []
        for file in listdir(self.raw_dir):
            if file.endswith('.csv') and "Stations" not in file:
                files.append(path.join(self.raw_dir, file))
        return files


class DCBikeSystem(BikeSystem):
    city = "DC"
    loader = CSVLoader.load_cabi

    def get_files(self):
        return [
            path.join(self.raw_dir, f) for f in listdir(self.raw_dir)
            if f.endswith(".csv")
        ]
