#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sqlite3
import plotly.graph_objs as go
from datetime import datetime, timedelta

# def sourcesColor(s):
#     colors = {
#         'Aged seasalt': "#00b0ff",
#         'Aged seasalt/HFO': "#8c564b",
#         'Biomass burning': "#92d050",
#         'Dust': "#dac6a2",
#         'Fresh seasalt': "#00b0f0",
#         'HFO': "#70564b",
#         'HFO (stainless)': "#8c564b",
#         'Industries': "#7030a0",
#         'Mineral dust': "#dac6a2",
#         'Nitrate rich': "#ff7f2a",
#         'Primary biogenic': "#ffc000",
#         'Resuspended dust': "#dac6a2",
#         'Road salt': "#00b0f0",
#         'Road traffic': "#000000",
#         'Seasalt': "#00b0f0",
#         'Secondary biogenic': "#8c564b",
#         'Secondary biogenic/HFO': "#8c564b",
#         'Sulfate rich': "#ff2a2a",
#         'Sulfate rich/HFO': "#ff2a2a",
#         'Anthropogenic SOA': "#8c564b",
#     }
#     if s not in colors.keys():
#         print("WARNING: no {} found in colors".format(s))
#         return "#666666"
#     return colors[s]

def get_sourceColor(source=None, SOURCES_like=False):
    if SOURCES_like:
        color ={
                "Road traffic": "#595959",
                "Traffic": "#595959",
                "Traffic_ind": "#595959",
                "Primary traffic": "#595959",
                "Traffic_exhaust": "#595959",
                "Traffic_dir": "#444444",
                "Traffic_non-exhaust": "#444444",
                "Oil/Vehicular": "#595959",
                "Biomass_burning": "#538134",
                "Biomass_burning1": "#538134",
                "Biomass_burning2": "#538134",
                "Sulfate_rich": "#ff0000",
                "Nitrate_rich": "#0000cc",
                "Secondary inorganics": "#0000cc",
                "Secondary_biogenic": "#8c564b",
                "Biogenic SOA": "#8c564b",
                "Anthropogenic SOA": "#8c564b",
                "Marine/HFO": "#8c564b",
                "Aged seasalt/HFO": "#8c564b",
                "Marine_biogenic": "#fc564b",
                "HFO": "#70564b",
                "HFO (stainless)": "#70564b",
                "Marine": "#ffbf00",
                "Marin": "#ffbf00",
                "Salt": "#9cc3e6",
                "Aged_salt": "#6f2f9f",
                "Fungal spores": "#00af4f",
                "Primary_biogenic": "#00af4f",
                "Biogenique": "#00af4f",
                "Biogenic": "#00af4f",
                "Dust": "#ff6500",
                "Crustal_dust": "#ff6500",
                "Industrial": "#ff65ff",
                "Indus/veh": "#ff65ff",
                "Arcellor": "#ff65ff",
                "Siderurgie": "#ff65ff",
                "Plant debris": "#2aff80",
                "Plant_debris": "#2aff80",
                "Débris végétaux": "#2aff80",
                "Choride": "#80e5ff",
                "PM other": "#cccccc",
                "Traffic/dust (Mix)": "#333333",
                "SOA/sulfate (Mix)": "#6c362b",
                "nan": "#ffffff"
                }
    else:
        color = {
                "Traffic": "#000000",
                "Road traffic": "#000000",
                "Primary traffic": "#000000",
                "Traffic_ind": "#000000",
                "Traffic_exhaust": "#000000",
                "Traffic_dir": "#444444",
                "Traffic_non-exhaust": "#444444",
                "Oil/Vehicular": "#000000",
                "Road traffic/oil combustion": "#000000",
                "Biomass_burning": "#92d050",
                "Biomass burning": "#92d050",
                "Biomass_burning1": "#92d050",
                "Biomass_burning2": "#92d050",
                "Sulfate_rich": "#ff2a2a",
                "Sulfate rich": "#ff2a2a",
                "Nitrate_rich": "#217ecb", # "#ff7f2a",
                "Nitrate rich": "#217ecb", # "#ff7f2a",
                "Secondary inorganics": "#0000cc",
                "Secondary_biogenic": "#ff7f2a", # 8c564b",
                "Secondary biogenic": "#ff7f2a", # 8c564b",
                "Biogenic SOA": "#8c564b",
                "Anthropogenic SOA": "#8c564b",
                "Marine/HFO": "#a37f15", #8c564b",
                "Aged seasalt/HFO": "#8c564b",
                "Marine_biogenic": "#fc564b",
                "HFO": "#70564b",
                "HFO (stainless)": "#70564b",
                "Marine": "#33b0f6",
                "Marin": "#33b0f6",
                "Salt": "#00b0f0",
                "Seasalt": "#00b0f0",
                "Sea/road salt": "#00b0f0",
                "Fresh seasalt": "#00b0f0",
                "Aged_salt": "#97bdff", #00b0f0",
                "Aged seasalt": "#97bdff", #00b0f0",
                "Fungal spores": "#ffc000",
                "Primary_biogenic": "#ffc000",
                "Primary biogenic": "#ffc000",
                "Biogenique": "#ffc000",
                "Biogenic": "#ffc000",
                "Dust": "#dac6a2",
                "Mineral dust": "#dac6a2",
                "Crustal_dust": "#dac6a2",
                "Industrial": "#7030a0",
                "Industries": "#7030a0",
                "Indus/veh": "#5c304b",
                "Industry/traffic": "#5c304b", #7030a0",
                "Arcellor": "#7030a0",
                "Siderurgie": "#7030a0",
                "Plant debris": "#2aff80",
                "Plant_debris": "#2aff80",
                "Débris végétaux": "#2aff80",
                "Choride": "#80e5ff",
                "PM other": "#cccccc",
                "Traffic/dust (Mix)": "#333333",
                "SOA/sulfate (Mix)": "#6c362b",
                "Sulfate rich/HFO": "#8c56b4",
                "nan": "#ffffff"
                }
    color = pd.DataFrame(index=["color"], data=color)
    if source:
        if source not in color.keys():
            print("WARNING: no {} found in colors".format(source))
            return "#666666"
        return color.loc["color", source]
    else:
        return color


def add_month(df, season=False):
    """Add a season column to the DataFrame df from its index or column 'date'.

    :df: A pandas DataFrame
    :season: Boolean, default False. Either or not add a season column.
    :returns: df_tmp, a copy of df with a new column

    """

    month_to_season = {1:'DJF', 2:'DJF', 3:'MAM', 4:'MAM', 5:'MAM', 6:'JJA',
                       7:'JJA', 8:'JJA', 9:'SON', 10:'SON', 11:'SON', 12:'DJF'}
    number_to_name = {1: "Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May",
                      6: "Jun", 7:"Jul", 8:"Aug", 9:"Sep",
                      10:"Oct", 11:"Nov", 12:"Dec"}

    df_tmp = df.copy()
    # ensure we have date in index
    if 'date' not in df_tmp.columns:
        print("No date given")
        return
    else:
        df_tmp.date = pd.to_datetime(df_tmp["date"])

    df_tmp["month"] = df_tmp.date.apply(lambda x: x.month)
    df_tmp.sort_values(by="month", inplace=True)
    if season:
        df_tmp["season"] = df_tmp["month"].replace(month_to_season)
    else:
        df_tmp["month"].replace(number_to_name, inplace=True)
    return df_tmp

def fractionaldate2datetime(start):
    """Convert a fractional date (2012.7) to the proper datetime object

    :start: the given date in a fractional format (e.g. 2012.7)
    :returns: datetime object of the fractional date
    """
    year = int(start)
    rem = start - year
    base = datetime(year, 1, 1)
    result = base + timedelta(seconds=(base.replace(year=base.year + 1) -
                                       base).total_seconds() * rem)
    return result

def datetime2fractionaldate(date):
    """Convert a datetime object to fractional date (2012.7)

    :date: the datetime
    :returns: fractional date (float)
    """
    year = date.year
    boy = datetime(year, 1, 1)
    eoy = datetime(year+1, 1, 1)
    result = year + (date- boy).total_seconds() / (eoy - boy).total_seconds()
    return result




def plot_ts(df, station, var, groupby):
    """Set a trace for plotly of the timeserie var in df for the given station,
    grouped by groupby.

    :df: a pandas dataframe with a 'date' column
    :station: string. The name of the station
    :var: list. The variables to plot
    :groupby: list. The columns to group by.
    :returns: a list of plotly traces
    """
    traces=[]
    if len(groupby) != 0:
        for v in var:
            for group in groupby:
                for groupName, dfgroup in df.groupby(group):
                    if all(dfgroup.loc[:, v].isnull()):
                        continue
                    dfgroup = dfgroup.sort_values(by="date")
                    traces.append(go.Scatter(
                        x=dfgroup.loc[:, "date"],
                        y=dfgroup.loc[:, v],
                        mode="lines+markers",
                        name="{}-{}-({})".format(station, v, groupName)
                    ))
    else:
        for v in var:
            dfgroup = df.sort_values(by="date")
            traces.append(go.Scatter(
                x=dfgroup.loc[:, "date"],
                y=dfgroup.loc[:, v],
                mode="lines+markers",
                name="{}-{}".format(station, v)
            ))
    return traces

def plot_box(df, trace_name, x_var, y_var, groupby=None, plot_type="box"):
    """Set a trace for plotly of the timeserie var in df for the given station,
    grouped by groupby.

    :df: DataFrame to plot
    :trace_name: Either station or season
    :var: list of string, the names of the columns variables to plot
    :groupby: list, column to groupby
    :x_var: string, the name of the column to use for the x-axis variable
    :plot_type: {"box", "bar"}, default "box", either to plot a boxplot or a barplot
    :returns: a list of plotly traces
    """
    traces=[]
    df = df.sort_values(by="station")
    if len(groupby) != 0:
        for v in y_var:
            for group in groupby:
                for groupName, dfgroup in df.groupby(group):
                    if plot_type == "box":
                        traces.append(go.Box(
                            y=dfgroup.loc[:, v],
                            x=dfgroup.loc[:, x_var],
                            name="{}-{}-({})".format(trace_name, v, groupName)
                        ))
                    elif plot_type == "bar":
                        dftmp = dfgroup.groupby(x_var).mean()
                        traces.append(go.Bar(
                            y=dftmp[v],
                            x=dftmp.index,
                            name="{}-{}-({})".format(trace_name, v, groupName)
                        ))
    else:
        for v in y_var:
            if plot_type == "box":
                traces.append(go.Box(
                    y=df.loc[:, v],
                    x=df.loc[:, x_var],
                    name="{}-{}".format(trace_name, v)
                ))
            elif plot_type == "bar":
                dftmp = df.groupby(x_var).mean()
                traces.append(go.Bar(
                    y=dftmp[v],
                    x=dftmp.index,
                    name="{}-{}".format(trace_name, v)
                ))

    return traces

def replace_QL(dftmp):
    """Replace the -1 and -2 in the dataframe by the appropriate DL and QL
    values

    The change are done inplace.

    :dftmp: pandas DataFrame
    """
    stations = dftmp.station.unique()
    conn = sqlite3.connect(settings.BDDPM) # BDDPM must be defined in local_settings.py
    QLtmp = pd.read_sql(
        'SELECT * FROM QL \
        WHERE station IN ("{}") AND "sample ID" LIKE "%QL%";'.format('", "'.join(stations)), conn)
    conn.close()
    QLtmp = QLtmp.apply(pd.to_numeric, errors='ignore').dropna(how="all", axis=1)
    for station in stations:
        QLtmpmean = QLtmp[QLtmp.station==station].mean()
        to_replace = {
            c: {-2: QLtmpmean[c]/2, -1: QLtmpmean[c]/2} for c in QLtmpmean.index
        }
        for c in dftmp.columns:
            if (c in to_replace.keys()) and (pd.notna(to_replace[c][-1])):
                idx = dftmp.station == station
                dftmp.loc[idx, c] = dftmp.loc[idx, c].clip_lower(to_replace[c][-1])
