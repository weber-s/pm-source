# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import os
import urllib
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

from utilities import *
from app_components_SOURCES import *
# from .deltatool import *

def get_contribution(contrib, profile, sources, species, stations):
    contribtmp = contrib.set_index(["station", "date"], drop=True)
    profiletmp = profile.set_index(["station", "specie"], drop=True)
    PM = pd.DataFrame(index=contribtmp.index)
    if len(sources)>0:
        df = pd.DataFrame(index=contribtmp.index)
        df = (contribtmp * profiletmp.loc[(slice(None), "PM10"), :].reset_index().set_index("station"))
        PM = PM.merge(df, right_index=True, left_index=True, how="inner")

    if len(species)>0:
        df = pd.DataFrame(index=contribtmp.index)
        for specie in species:
            df[specie] = (contribtmp \
                     * profiletmp.loc[(slice(None), specie), :]\
                     .reset_index()\
                     .set_index("station")\
                     .drop("specie", axis=1)
                    ).sum(axis=1)
        PM = PM.merge(df, right_index=True, left_index=True, how="inner")
        PM[species] = PM[species].replace({0: pd.np.nan})

    dftmp = PM.loc[(stations, slice(None)), sources+species] 
    dftmp.reset_index(inplace=True)

    return dftmp

# BDD connexion ================================================================

DBPATH = "./DB_SOURCES.db"
conn = sqlite3.connect(DBPATH)
contrib = pd.read_sql(
    "SELECT * FROM contributions_constrained;",
    con=conn,
    parse_dates=["date"]
)
# contrib.set_index(['station', 'date'], drop=True, inplace=True)
contrib.drop("index", inplace=True, axis=1)
profile = pd.read_sql(
    "SELECT * FROM profiles_constrained;",
    con=conn
)
# profile.set_index(['station', 'specie'], drop=True, inplace=True)
profile.drop("index", inplace=True, axis=1)

dfmap = pd.read_sql(
    'SELECT * FROM metadata_station;',
    con=conn
)

SID = pd.read_sql(
    "SELECT * FROM SID;",
    con=conn,
)

PD = pd.read_sql(
    "SELECT * FROM PD;",
    con=conn,
)
conn.close()
## =============================================================================
SID.set_index(["source", "station"], inplace=True)
PD.set_index(["source", "station"], inplace=True)
if "index" in SID.columns:
    SID.drop("index", axis=1, inplace=True)
if "index" in PD.columns:
    PD.drop("index", axis=1, inplace=True)


STATIONS = profile["station"].unique()

BASE_VAR_SP = ["date", "station"]
BASE_VAR_SRC = ["date", "station"]

SELECTEDSTATION = set()

# do not add species to plot when we already have too many...
tooManyPlot = 30
minSample = 40

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            id="main",
            children=[
                #first column
                html.Div(
                    id="first-column",
                    children=[
                        html.Div([
                            station_dropdown_component(STATIONS),
                            specie_dropdown_component,
                            source_dropdown_component,
                        ]),

                        html.Div([
                            html.Div(
                                get_daterange_slider(
                                    contrib['date']
                                ),
                                style={'margin': '0 20px 20px 20px'}
                            ),

                        ], style={'display':'inline-block', 'width':'100%'}),

                        dcc.Graph(
                            id = "map-graph",
                            figure = {
                                "data": get_map_data(dfmap),
                                "layout": get_map_layout()
                            }
                        ),

                        html.Br(),

                        html.Div([
                            gettinghelp_component
                        ])
                    ],
                    style = {"display": "inline-block",
                             "width": "45%",
                             "margin-left":"10px",
                             "horizontal-align":"left",
                             'vertical-align': 'top'}
                ),
                # second column
                html.Div(
                    id="second-column",
                    children=[
                        dcc.Tabs(
                            id="tab_tsordt",
                            value=1,
                            children=[
                                dcc.Tab(label="TimeSerie", value=1,
                                        children=[timeserie_component]
                                       ),
                                dcc.Tab(label="Profile", value=2,
                                        children=[
                                            profile_component,
                                            deltatool_component
                                            ]
                                       )
                            ]
                        ),

                    ],
                    style={"display": "inline-block",
                           "width": "50%",
                           "margin-left":"30px",
                           "horizontal-align":"right",
                           'vertical-align': 'top'}
                )
            ],
            style={'width': '100%', 'padding':'20px'}
        ),
    ]
)


external_css = ["https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
                "https://codepen.io/chriddyp/pen/bWLwgP.css",
               ]

for css in external_css:
    app.css.append_css({"external_url": css})


@app.callback(Output('specie-dropdown', 'options'),
              [Input('station-dropdown', 'value')])
def set_specie_option(stations):
    species = profile.loc[profile["station"].isin(stations), "specie"].unique()
    species = set(species) - set(BASE_VAR_SP)
    species = list(species)
    species.sort()
    return [{'label': i, 'value': i} for i in species]

@app.callback(Output('source-dropdown', 'options'),
              [Input('station-dropdown', 'value')])
def set_source_option(stations_dd):
    sources = []
    sources = profile.loc[profile["station"].isin(stations_dd)].dropna(axis=1, how='all').columns
    sources = set(sources) - set(BASE_VAR_SRC)
    sources = list(sources)
    if "specie" in sources:
        sources.remove("specie")
    sources.sort()

    return [{'label': i, 'value': i} for i in sources]

def update_selected_station(map4station, dropdown4station):
    """
    Update the SELECTEDSTATION variable according to both the map and the
    dropwdown list of station.
    """
    #TODO: lasso selection
    # if values1:
    #     for point in values1["points"]:
    #         s = point["text"]
    #         print(s)
    #         if s in SELECTEDSTATIONMAP:
    #             SELECTEDSTATIONMAP.remove(s)
    #         else:
    #             SELECTEDSTATIONMAP.append(s)

    # reset selected station and repopulate it
    if not map4station:
        SELECTEDSTATION.clear()
    # point selected on the map
    if map4station:
        for point in map4station["points"]:
            s = point["text"]
            if s in SELECTEDSTATION:
                SELECTEDSTATION.remove(s)
                dropdown4station.remove(s)
            else:
                SELECTEDSTATION.update([s])
    # add also station mannualy selected
    SELECTEDSTATION.update(dropdown4station)

    # no return. SELECTEDSTATION is a static variable

@app.callback(Output('station-dropdown', 'value'),
              [Input('map-graph','clickData')],
              [State('station-dropdown', 'value')])
def update_dropdown_station_selected(values, stations):
    update_selected_station(values, stations)
    return list(SELECTEDSTATION)

@app.callback(Output('map-graph', 'figure'),
              [Input('station-dropdown', 'value')],
              [State('map-graph', 'figure')])
def update_map_station_selected(stations, figure):
    update_selected_station(None, stations)
    # TODO: update_selected_station is called even if the stations variable is
    # unchanged.

    data = get_map_data(dfmap)
    idx = dfmap["abbrv"].isin(SELECTEDSTATION)
    data.append(
        dict(
            type = 'scattergeo',
            lon = dfmap.loc[idx,"longitude"],
            lat = dfmap.loc[idx,"latitude"],
            text = dfmap.loc[idx,"abbrv"],
            name = ""
        )
    )
    figure = {"data":data, "layout": get_map_layout()}
    return figure

@app.callback(Output('ts-graph', 'figure'),
              [Input('station-dropdown', 'value'),
              Input('specie-dropdown', 'value'),
              Input('source-dropdown', 'value')])
def update_ts_graph(stations, species, sources):
    traces=[]
    returnError = {'data': traces,
                   'layout': {'title': 'Time serie(s)'}
                  }

    if (len(species) + len(sources)) == 0:
        print("TS: len(species+sources)==0")
        return returnError

    nbPlot = 0 #len(stations) * len(set(species)-set(notNumeric))
    if nbPlot > tooManyPlot:
        print("TS: too many things to plot... skip it", nbPlot)
        return returnError

    dfdt = get_contribution(contrib, profile, sources, species, stations)

    if len(dfdt.columns)==2:
        print("TS: Only date and station")
        return returnError
    dfdt["labels"] = pd.np.nan
    stations = dfdt.station.unique()
    # species = dfdt.columns

    dfdt["labels"].fillna(value=pd.np.nan, inplace=True)

    # should never happen... but just in case
    if "date" not in dfdt.columns:
        print("TS: no date given")
        return returnError

    species = set(species) - set(BASE_VAR_SP)
    sources = set(sources) - set(BASE_VAR_SRC)

    for station in stations:
        dftmp = dfdt[dfdt["station"]==station]
        for toplot, var in zip(("species", "sources"), (species, sources)):
            if len(var)==0:
                continue
            groupby = []
            if toplot == "species":
                if any(dftmp["labels"].notnull()):
                    groupby += ["labels"]
            elif toplot == "sources":
                groupby += [] #"programme PMF"]
            traces += [i for i in plot_ts(dftmp, station, var, groupby)]

    to_return = {
        'data': traces,
        'layout': go.Layout(
            yaxis={"title": 'µg/m3'},
            showlegend=True,
            title="Time serie(s)",
            margin=go.layout.Margin(
                l=50,
                r=00,
                b=50,
                t=50,
                pad=0
            ),
            legend=dict(orientation="h")
        )
    }

    return to_return 

@app.callback(Output('box-graph', 'figure'),
              [Input('tab-boxplot', 'value'),
              Input('boxplot_options', 'value'),
              Input('boxplot_groubpy_options', 'value'),
              Input('specie-dropdown', 'value'),
              Input('source-dropdown', 'value'),
              Input('station-dropdown', 'value')],
             [State('tab_tsordt', 'value')])
def update_box_grah(temporality, plots_options, groupby_var, species,
                    sources, stations, tabselected):
    """Seasonal boxplot or barplot"""
    traces=[]
    returnError = {'date': traces,
                   'layout': {'title': 'Seasonal dispersion'}
                  }
    if tabselected == 2:
        return returnError
    if (len(species) + len(sources)) == 0:
        print("BOX: no data to plot")
        return returnError

    dfdt = get_contribution(contrib, profile, sources, species, stations)

    stations = dfdt.station.unique()

    species = set(species) - set(BASE_VAR_SP)
    sources = set(sources) - set(BASE_VAR_SRC)

    nbPlot = len(stations) * (len(species) +len(sources))
    if nbPlot > tooManyPlot:
        print("BOX: too many things to plot... skip it", nbPlot)
        return returnError

    # check if we want monthly or seasonal group
    #TODO: may use directly the label of the tab + refactoring the add_month
    #      function
    month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                  "Oct", "Nov", "Dec"]
    season_list = ["DJF", "MAM", "JJA", "SON"]

    if temporality == 1:
        dfdt = add_month(dfdt, season=True)
        x_var = "season"
    elif temporality == 2:
        dfdt = add_month(dfdt)
        x_var = "month"

    # select data and add traces
    if groupby_var == "date":
        for station in stations:
            dftmp = dfdt[dfdt["station"]==station]

            for toplot, var in zip(("species", "sources"), (species, sources)):
                if len(var)==0:
                    continue
                groupby = []
                if 'boxplot' in plots_options:
                    plot_type = "box"
                elif 'barplot' in plots_options:
                    plot_type = "bar"
                traces += [i for i in plot_box(dftmp, station,
                                               x_var=x_var,
                                               y_var=var,
                                               groupby=groupby,
                                               plot_type=plot_type
                                              )]
    elif groupby_var == "site":
        if x_var == "season":
            xgroup_vars = season_list
        elif x_var == "month":
            xgroup_vars = month_list

        for xgroup_var in xgroup_vars:
            dftmp = dfdt[dfdt[x_var]==xgroup_var]
            # dftmp["programme PMF"].replace({"--": pd.np.nan}, inplace=True)

            for toplot, var in zip(("species", "sources"), (species, sources)):
                if len(var)==0:
                    continue
                groupby = []
                if toplot == "species":
                    if ("labels" in dftmp.columns) and (any(dftmp["labels"].notnull())):
                        groupby += ["labels"]
                elif toplot == "sources":
                    groupby += [] #["programme PMF"]
                if 'boxplot' in plots_options:
                    plot_type = "box"
                elif 'barplot' in plots_options:
                    plot_type = "bar"
                traces += [i for i in plot_box(dftmp, xgroup_var,
                                               x_var="station",
                                               y_var=var,
                                               groupby=groupby,
                                               plot_type=plot_type
                                              )]

    xticklabels = [i for i in month_list if i in dfdt.loc[:, x_var].unique()]

    return {
        'data': traces,
        'layout': go.Layout(
            yaxis={"title": "µg/m3"},
            xaxis={'categoryorder': 'array',
                   'categoryarray': xticklabels},
            showlegend=True,
            boxmode='group',
            margin=go.layout.Margin(
                l=50,
                r=00,
                b=50,
                t=50,
                pad=0
            ),
            legend=dict(orientation="h")
        )
    }


@app.callback(Output('totalspeciesum-graph', 'figure'),
              [Input('source-dropdown', 'value'),
               Input('station-dropdown', 'value')])
def update_totalspecisum_graph(sources, stations):
    data = []
    if len(stations) == 0:
        return {
            'data': [],
            "layout": {"title": "Contribution to total specie sum"}
        }

    idx = profile["station"].isin(stations)
    d = profile[idx]
    for s in sources:
        data.append(go.Box(
            x=d["specie"],
            y=d[s]/d.sum(axis=1).values *100,
            name=s)
        )
    # specie to plot
    carboneous = ["OC*", "EC"]
    ions = ["Cl-", "NO3-", "SO42-", "Na+", "NH4+", "K+", "Mg2+", "Ca2+"]
    organics = [
        "MSA", "Polyols", "Levoglucosan", "Mannosan",
    ]
    metals = [
        "Al", "As", "Ba", "Cd", "Co", "Cr", "Cs", "Cu", "Fe", "La", "Mn",
        "Mo", "Ni", "Pb", "Rb", "Sb", "Se", "Sn", "Sr", "Ti", "V", "Zn"
    ]
    keep_index = ["PM10"] + carboneous + ions + organics + metals

    to_return =  {
        'data': data,
        'layout': go.Layout(
            yaxis={
                "title": "% of total specie sum",
                "range": [0, 100]
                  },
            xaxis={'categoryorder': 'array',
                   'categoryarray': keep_index},
            showlegend=True,
            boxmode='group',
            margin=go.layout.Margin(
                l=50,
                r=00,
                b=50,
                t=50,
                pad=0
            ),
            legend=dict(orientation="h")
        )
    }

    return to_return

@app.callback(Output('concentration-graph', 'figure'),
              [Input('source-dropdown', 'value'),
               Input('station-dropdown', 'value')])
def update_concentration_graph(sources, stations):
    data = []
    if len(stations)==0:
        return {
            'data': [],
            "layout": {"title": "Contribution to total specie sum"}
        }

    d = profile.set_index(["station", "specie"])
    d = d.loc[stations]
    d = d / d.loc[(slice(None), "PM10"), :]\
            .reset_index()\
            .set_index("station")\
            .drop("specie", axis=1)
    d = d.reset_index()
    d.replace({0: pd.np.nan}, inplace=True)
    for s in sources:
        data.append(go.Box(
            x=d["specie"],
            y=d.loc[d["station"].isin(stations), s],
            name=s)
        )
    # specie to plot
    carboneous = ["OC*", "EC"]
    ions = ["Cl-", "NO3-", "SO42-", "Na+", "NH4+", "K+", "Mg2+", "Ca2+"]
    organics = [
        "MSA", "Polyols", "Levoglucosan", "Mannosan",
    ]
    metals = [
        "Al", "As", "Ba", "Cd", "Co", "Cr", "Cs", "Cu", "Fe", "La", "Mn",
        "Mo", "Ni", "Pb", "Rb", "Sb", "Se", "Sn", "Sr", "Ti", "V", "Zn"
    ]
    keep_index = ["PM10"] + carboneous + ions + organics + metals

    to_return =  {
        'data': data,
        'layout': go.Layout(
            yaxis={"title": "g/g of PM10",
                   "type": "log"},
            xaxis={'categoryorder': 'array',
                   'categoryarray': keep_index},
            showlegend=True,
            boxmode='group',
            margin=go.layout.Margin(
                l=50,
                r=00,
                b=50,
                t=50,
                pad=0
            ),
            legend=dict(orientation="h")
        )
    }

    return to_return
                
@app.callback(Output('deltatool-graph', 'figure'),
              [Input('source-dropdown', 'value'),
               Input('station-dropdown', 'value')])
def update_deltatool_graph(sources, stations):
    traces = []
    to_return =  {
        'data': traces,
        'layout': go.Layout(
            hovermode="closest",
            yaxis={
                "title": "PD",
                "range": [0, 1],
                "scaleratio": 1
            },
            xaxis={
                "title": "SID",
                "range": [0, 1.5],
                "scaleanchor": "y"
            },
            showlegend=True,
            margin=go.layout.Margin(
                l=50,
                r=00,
                b=50,
                t=50,
                pad=0
            ),
            legend=dict(orientation="v"),
            shapes=[
                {
                    'type': 'rect',
                    'x0': 0,
                    'y0': 0,
                    'x1': 1,
                    'y1': 0.6,
                    'line': {
                        'width': 0,
                        },
                    'fillcolor': 'rgba(0, 255, 0, 0.1)',
                    },
                ]
        )
    }

    if len(sources)==0:
        return to_return 

    x = SID.loc[(sources, stations), stations].reset_index()\
            .melt(id_vars=["source", "station"])\
            .set_index(["source", "station"])\
            .loc[sources]  
    y = PD.loc[(sources, stations), stations].reset_index()\
            .melt(id_vars=["source", "station"])\
            .set_index(["source", "station"])\
            .loc[sources]  

    for source in sources:
        text = x.xs(source, level="source")["variable"] + "-" + x.loc[source].index.get_level_values("station")
        traces.append(
            go.Scatter(
                x=x.xs(source, level="source")["value"],
                y=y.xs(source, level="source")["value"],
                mode="markers",
                marker=go.scatter.Marker(
                    color=get_sourceColor(source),
                    size=14
                ),
                hovertext=text,
                name=source,
            )
        )
    to_return["data"] = traces

    return to_return



if __name__ == '__main__':
    app.run_server(debug=True)
