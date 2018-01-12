import pandas as pd
import timeit

class CSVLoader:
    @classmethod
    def load_file(cls, file, name_map=None):
        print("Loading %s ..." % file)
        start = timeit.default_timer()
        df = pd.read_csv(file)
        df.rename(columns=name_map, inplace=True)
        for ext_col in ["birthyear", "gender", "usertype"]:
            if ext_col not in df.columns:
                df[ext_col] = None
        df["starttime"] = pd.to_datetime(df["starttime"])
        df["stoptime"] = pd.to_datetime(df["stoptime"])
        df_new = df[[
            "starttime", "stoptime", "startstation", "endstation", "usertype",
            "birthyear", "gender"
        ]]
        end = timeit.default_timer()
        print("Finished in %f seconds." % (end - start))
        return df_new

    @classmethod
    def load_cabi(cls, file):
        name_map = {
            "Start date": "starttime",
            "Start time": "starttime",
            "End date": "stoptime",
            "Start station": "startstation",
            "Start Station": "startstation",
            "End station": "endstation",
            "End Station": "endstation",
            "Member Type": "usertype",
            "Member type": "usertype",
            "Subscription type": "usertype",
        }
        return cls.load_file(file, name_map)

    @classmethod
    def load_citibike(cls, file):
        return cls.load_hubway(file)

    @classmethod
    def load_Chattanooga(cls, file):
        name_map = {
            "StartStationName": "startstation",
            "EndStationName": "endstation",
            "StartDateTime": "starttime",
            "EndDateTime": "stoptime",
            "Start station name": "startstation",
            "End station name": "endstation",
            "MemberType": "usertype",
        }
        return cls.load_file(file, name_map)

    @classmethod
    def load_hubway(cls, file):
        name_map = {
            "start station name": "startstation",
            "end station name": "endstation",
            "birth year": "birthyear",
            "Start date": "starttime",
            "End date": "stoptime",
            "Start station name": "startstation",
            "End station name": "endstation",
            "Bike number": "bikeid",
            "Member type": "usertype",
            "Gender": "gender",
            "Start Time": "starttime",
            "Stop Time": "stoptime",
            "Start Station Name": "startstation",
            "End Station Name": "endstation",
            "Birth Year": "birthyear",
            "User Type": "usertype"
        }
        return cls.load_file(file, name_map)

    @classmethod
    def load_divvy(cls, file):
        name_map = {
            "from_station_name": "startstation",
            "to_station_name": "endstation",
            "birthday": "birthyear",
            "start_time": "starttime",
            "end_time": "stoptime"
        }
        return cls.load_file(file, name_map)