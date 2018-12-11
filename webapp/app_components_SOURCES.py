import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd

from datetime import datetime, timedelta

def datetime2fractionaldate(date):
    """
    Convert a datetime object to fractional date (2012.7)
    """
    year = date.year
    boy = datetime(year, 1, 1)
    eoy = datetime(year+1, 1, 1)
    result = year + (date- boy).total_seconds() / (eoy - boy).total_seconds()
    return result

def station_dropdown_component(stations):
    return html.Div(
        children=[
            html.Label('Station'),
            dcc.Dropdown(
                id="station-dropdown",
                options=[{'label': s, 'value': s} for s in stations],
                multi=True,
                value=stations
            )
        ],
        style={"position": "relative"}
    )


def get_map_data(dfmap):
    """Get the map data given by dfmap

    :dfmap: pandas DataFrame
    :returns: list of plotly trace
    """
    DATA_MAP = [ dict(
        type= 'scattergeo',
        lon=dfmap['longitude'],
        lat=dfmap['latitude'],
        text=dfmap['abbrv'],
        mode = 'markers',
        name = ''
        )
    ]
    return DATA_MAP

def get_map_layout():
    """Return the layout for the map.

    :returns: dict
    """
    LAYOUT_MAP = dict(
        showlegend = False,
        margin = go.layout.Margin(l=20, r=20, b=20, t=20, pad=2),
        geo = dict(
            scope = 'world',
            showland = True,
            landcolor = "rgb(212, 212, 212)",
            subunitcolor = "rgb(255, 255, 255)",
            countrycolor = "rgb(255, 255, 255)",
            showlakes = False,
            lakecolor = "rgb(255, 255, 255)",
            showsubunits = True,
            showcountries = True,
            resolution = 50,
            projection = dict(
                type = 'equirectangular',
                rotation = dict(
                    lon = 0
                )
            ),
            lonaxis = dict(
                showgrid = True,
                gridwidth = 0.5,
                range= [ -5.0, 15.0 ],
                dtick = 5
            ),
            lataxis = dict (
                showgrid = True,
                gridwidth = 0.5,
                range= [ 40.0, 55.0 ],
                dtick = 5
            )
        ),
    )
    return LAYOUT_MAP


specie_dropdown_component =  html.Div(
    children=[
        html.Label('Species'),

        dcc.Dropdown(
            id='specie-dropdown',
            options=[],
            multi=True,
            value=[]
        )
    ],
    style={"position": "relative"}
)

source_dropdown_component = html.Div(
    children=[
        html.Label('Sources'),

        dcc.Dropdown(
            id='source-dropdown',
            options=[],
            multi=True,
            value=[]
        )
    ],
    style={"position": "relative"},
)

options_component = html.Div(children=[
    html.Div(
        id="selectall",
        children=[
            dcc.Checklist(
                id='selectall_check',
                options=[
                    {'label': 'all station', 'value': 'allStation'},
                    {'label': 'all sources', 'value': 'allSource'},
                ],
                values=[],
                labelStyle={'display': 'inline-block',
                            'margin': '0 5px'}
            )
        ],
        style={'display': 'inline-block',
               'margin': '0 10px'}
    )
])

datatable_component = html.Div(
    children=[
        html.Div(
            dt.DataTable(
                rows=[{}], # initialise the rows
                row_selectable=True,
                filterable=True,
                sortable=True,
                editable=False,
                selected_row_indices=[],
                id='datatable'
            ),
            style={"padding":"5px","width": "95%","margin":"auto"}
        ),

        # html.Br(),
        #
        # html.Div(
        #     children=[
        #         html.Button(id='refresh-button',children="Refresh"),
        #         html.A(children='Download',
        #                id='download-data',
        #                download="rawdata.csv",
        #                href="",
        #                target="_blank",
        #                style={"padding":"10px"}
        #               )
        #     ], style={"margin":"3px"}
        # ),
    ], style={"border-style": "solid","border-width": "thin",
              "margin": "3px auto 3px"}
)

gettinghelp_component = html.Div(
    children=[
        dcc.Markdown(
'''
### The SOURCES programme

This app is the interactive visualization of the SOURCES programme, founded by the
ADEME, conduct by
[IGE](https://www.ige-grenoble.fr) and [INERIS](https://www.ineris.fr). 
Please refer to the
[report](https://www.lcsqa.org/fr/rapport/2016/ineris/traitement-harmonise-jeux-donnees-multi-sites-etude-sources-pm-positive-matrix-f)
(french) or article ([english](https://example.org)) for a detailed discussion.

The app is developped and maintained by Samuël Weber.

### Dash

This app is written with [Dash](https://plot.ly/dash/), so the graph are
interactive and responsive. *Hover* over points to see their values, *click* on
legend items to toggle traces, *click and drag* to zoom, *hold down shift, and
click and drag* to pan.



'''
        )
    ], style={"display": "block",
              "width": "100%", 
              "vertical-align":"top"}
)

boxplot_options = html.Div(
    children=[
        html.Div(
            children=[
                html.Label('Graph type: '),
                dcc.RadioItems(
                    id='boxplot_options',
                    options=[
                        {'label': 'boxplot', 'value': 'boxplot'},
                        {'label': 'barplot (mean)', 'value': 'barplot'}
                    ],
                    value='boxplot',
                    labelStyle={'display': 'inline-block',
                                'margin': '0 0 0 5px',
                                'padding': '0 0 0 5px'}
                )
            ],
            style={'display': 'flex', 'width': '45%'}
        ),
        html.Div(
            children=[
                html.Label('Group by: '),
                dcc.RadioItems(
                    id='boxplot_groubpy_options',
                    options=[
                        {'label': 'date', 'value': 'date'},
                        {'label': 'site', 'value': 'site'}
                    ],
                    value='date',
                    labelStyle={'display': 'inline-block',
                                'margin': '0 0 0 5px',
                                'padding': '0 0 0 5px'}
                )
            ],
            style={'display': 'flex', 'width': '45%'}
        )
    ],
)

timeserie_component = html.Div(
    children=[
        # plots_options,
        html.Div(children=[
            dcc.Graph(
                id='ts-graph',
                figure={'data': [], 'layout': {'title': 'Time serie(s)'}}
            )
        ]),

        html.Div(children=[
            dcc.Tabs(
                value=1,
                id="tab-boxplot",
                children=[
                    dcc.Tab(label="Seasonal", value=1),
                    dcc.Tab(label="Monthly", value=2),
                ]
            ),
            boxplot_options,
            dcc.Graph(
                id='box-graph',
                figure={'data': [], 'layout': {'title': 'Seasonal variation'}}
            ),

        ])
    ]
)

profile_component = html.Div(
    children=[
        html.Div(children=[
            dcc.Tabs(
                value=1,
                id="tab-concentration",
                children=[
                    dcc.Tab(label="Rel. conc.", value=1, children=[
                        dcc.Graph(
                            id="concentration-graph",
                            figure={'data': [], "layout": {"title": "Relative concentration"}}
                        )
                    ]),
                    dcc.Tab(label="Total specie sum", value=2, children=[
                        dcc.Graph(
                            id="totalspeciesum-graph",
                            figure={'data': [], "layout": {"title": "Contribution to total specie sum"}}

                        )
                    ])
                ]
            ),

        ])
    ]
)

deltatool_component = html.Div(
        children=[
            html.Div(children=[
            dcc.Graph(
                id="deltatool-graph",
                figure={
                    'data': [], 
                    "layout": {
                        "title": "DeltaTool distance",
                        "shapes": [
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
                            }
                        ]
                    }
                }
                )
            ])
        ])

def get_daterange_slider(dates):
    if type(dates) !=  pd.core.series.Series:
        dates = pd.Series(dates)
    years = sorted(dates.apply(lambda x: x.year).unique())
    slider = dcc.RangeSlider(
        id="date_minmax",
        min=dates.apply(lambda x: x.year).min(),
        max=dates.apply(lambda x: x.year).max()+1,
        value=[datetime2fractionaldate(dates.min()), 
               datetime2fractionaldate(dates.max())+1],
        step=1/12,
        marks={str(year): str(year) for year in
               range(min(years),max(years)+1)}
    )
    return slider
