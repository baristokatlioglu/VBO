from dash.dependencies import Input, Output, State
import dash
from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from app import app
import numpy as np
import glob
from dash import callback_context


from func import (
    headshotCards,
    drawFigure,
    drawStats,
    team_perf,
    drawCard,
    top_card,
    matchup_info,
    current_team_stats,
    team_schedule,
    player_perf,
    performance_forecast_buttons,
    get_button_count,
)

hs = headshotCards("Phoenix Suns")
n_buttons = get_button_count("Phoenix Suns")

team_ = "Phoenix Suns"

layout = dbc.Container(
    [
        dcc.Store(id="store-id"),
        html.H2(["TEAM"], id="team"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.Card(
                            top_card("Team Worth: 123456$", "worth-cardbody"),
                            color="success",
                            inverse=True,
                        ),
                        id="worth-card1",
                    ),
                    id="worth",
                    width=6,
                    align="center",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.Card(
                            top_card(
                                "Devin Booker and Chris Paul named NBA All-Stars",
                                "news-card-body",
                            ),
                            color="danger",
                            inverse=True,
                        ),
                        id="worth-card2",
                    ),
                    id="worth",
                    width=6,
                    align="center",
                ),
            ],
            align="center",
            id="worth-row",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.CardBody(
                            [
                                drawCard("Phoenix Suns", 0),
                                drawCard("Phoenix Suns", 1),
                                drawCard("Phoenix Suns", 2),
                                drawCard("Phoenix Suns", 3),
                                drawCard("Phoenix Suns", 4),
                            ],
                            id="PlayerCard",
                        )
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        matchup_info("Phoenix Suns"),
                        dbc.Card(current_team_stats("Phoenix Suns"), id="table-card"),
                    ],
                    width=6,
                ),
            ],
            id="second-row",
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2(["SCHEDULE"], id="schedule"),
        html.Hr(),
        dbc.Row([dbc.Col([dbc.Card(team_schedule("Phoenix Suns"), id="table-card2")])]),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2(["PLAYER PERFORMANCES"], id="p_performance"),
        html.Hr(),
        dbc.Row([dbc.Col([dbc.Card(player_perf("Phoenix Suns"), id="table-card3")])]),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2(["PERFORMANCE FORECAST"], id="f_performance"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            performance_forecast_buttons("Phoenix Suns"),
                            id="forecast-card",
                            className="shadow-card",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(children=[], width=2, id="placeholder1"),
                dbc.Col(children=[], width=10, id="placeholder2"),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
    ],
    className="team-page-container",
)


@app.callback(
    Output("store-id", "data"),
    [Input(f"btn-nclicks-{i+1}", "n_clicks") for i in range(n_buttons)],
)
def func(*args):
    trigger = callback_context.triggered[0]
    return trigger["prop_id"].split(".")[0].split("-")[-1]


@app.callback(Output("placeholder1", "children"), [Input("store-id", "data")])
def player_performance(data, team=team_):
    if data == "":
        data = 1
    else:
        data = int(data)
    merged = pd.read_csv("data/merged.csv")
    merged = merged[(merged.TEAM == team) & (merged.SEASON_ID == "2021-22")]
    per = pd.read_csv("data/per.csv")
    per["NAME"] = per["FIRST_NAME"] + " " + per["LAST_NAME"]
    links = glob.glob(f"assets/top/{team}/*")
    files = pd.DataFrame({"LINK": links})
    files["NAME"] = files.LINK.apply(lambda x: x.split("\\")[1][:-4])
    names = per[(per.TEAM == team) & (per.SEASON_ID == "2021-22")].reset_index(
        drop=True
    )[["NAME", "PER"]]
    hs = names.merge(files, on="NAME", how="left").sort_values(by="NAME")
    per = per[(per.TEAM == team) & (per.SEASON_ID == "2021-22")]
    per["PPG"] = np.round(per["PTS"] / per["GP"], 2)
    per["RPG"] = np.round(per["REB"] / per["GP"], 2)
    per["APG"] = np.round(per["AST"] / per["GP"], 2)
    per = per[["NAME", "PPG", "PER"]].sort_values(by="NAME")
    per = per.reset_index()
    hs = hs.reset_index()
    return dbc.Card(
        [
            html.P(
                [hs.NAME[data - 1]],
                style={"font-family": "Inter, sans-serif", "margin-top": "10px"},
            ),
            html.Img(
                src=hs.LINK[data - 1],
                width=188,
                height=137,
                style={"max-height": "100%", "max-width": "100%"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    html.P("PPG"),
                                    per[per.NAME == hs.NAME[data - 1]].PPG.values[0],
                                ],
                                className="p-card-stats-card",
                            )
                        ],
                        className="p-card-stats",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    html.P("PER"),
                                    per[per.NAME == hs.NAME[data - 1]].PER.values[0],
                                ],
                                className="p-card-stats-card",
                            )
                        ],
                        className="p-card-stats",
                    ),
                ],
                className="StatsRow",
                align=True,
                justify=True,
            ),
        ],
        className="shadow-card",
    )

@app.callback(Output("placeholder2", "children"), [Input("store-id", "data")])
def per_forecast(data, team=team_):
    if data == "":
        data = 1
    else:
        data = int(data)
    merged = pd.read_csv("data/merged.csv")
    merged = merged[(merged.TEAM == team) & (merged.SEASON_ID == "2021-22")]
    per = pd.read_csv("data/per.csv")
    per["NAME"] = per["FIRST_NAME"] + " " + per["LAST_NAME"]
    links = glob.glob(f"assets/top/{team}/*")
    files = pd.DataFrame({"LINK": links})
    files["NAME"] = files.LINK.apply(lambda x: x.split("\\")[1][:-4])
    names = per[(per.TEAM == team) & (per.SEASON_ID == "2021-22")].reset_index(
        drop=True
    )[["NAME", "PER"]]
    hs = names.merge(files, on="NAME", how="left").sort_values(by="NAME")
    per = per[(per.TEAM == team) & (per.SEASON_ID == "2021-22")]
    per["PPG"] = np.round(per["PTS"] / per["GP"], 2)
    per["RPG"] = np.round(per["REB"] / per["GP"], 2)
    per["APG"] = np.round(per["AST"] / per["GP"], 2)
    per = per[["NAME", "PPG", "PER"]].sort_values(by="NAME")
    per = per.reset_index()
    hs = hs.reset_index()
    forecast = pd.read_csv('data/perf_forecast.csv')
    p_select = hs.NAME[data - 1]
    forecast = forecast[(forecast.NAME == p_select)]
    forecast['SEASON'] = forecast.SEASON_ID.apply(lambda x: int(x[:4])+1)
    lst = [(row[1].SEASON, row[1].PER)
           if row[1].SEASON_ID != '2021-22' else (row[1].SEASON,np.round(row[1].PRED, 2))
           for row in forecast.iterrows()]
    g = pd.DataFrame(lst)
    g.columns = ['year','per']
    fig = px.line(data_frame=g, x='year', y='per').update_layout(
        template="ggplot2",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        title_x=0.5,
        title_y=0.22,
        font=dict(size=18, color="white"),
        margin={"t": 0, "l": 0, "r": 0, "b": 0},
    )
    return dbc.Card(
        [
            dcc.Graph(
                figure=fig,
                config={"displayModeBar": False},
                className="Graph",
            )

        ],
        className="shadow-card",
    )