import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import subprocess
import platform
import threading
import time

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

# Define static graph controls
static_graph_controls = [
    dbc.CardGroup(
        [
            dbc.Label("Ips:"),
            dbc.Input(
                id="ips",
                value=None,
                type="text",
                placeholder="Select ips do you wanna see",
                className="mb-3",
                style={"width": "20vw","margin":"vw"}
            ),

            dbc.Button("Submit", color="primary",id="submit-button"),

            dcc.Store(id='n-clicks-store'),  # Armazena o valor anterior de n_clicks

            html.Div(id='output-div')

        ]
    ),
]

@app.callback(
    Output('output-div', 'children'),
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('ips', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, value):
    if n_clicks is None:
        return ""
    return f"You entered: {value}"


# Configure main app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.Header([html.H3("Dashboard")]),
        dbc.Card(dbc.Row([dbc.Col(c) for c in static_graph_controls]), body=True),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon1",
                                children=[
                                    dcc.Graph(
                                        id="radar-graph",
                                        config={
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines",
                                                "pan2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ]
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon2",
                                children=[
                                    dcc.Graph(
                                        id="events-shots",
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawline",
                                                "drawopenpath",
                                                "drawcircle",
                                                "drawrect",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines",
                                                "pan2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ],
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
            ],
            className="g-0",  # Remover espaçamento entre colunas se necessário
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon3",
                                children=[
                                    dcc.Graph(
                                        id="events-assists",
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawline",
                                                "drawopenpath",
                                                "drawcircle",
                                                "drawrect",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines",
                                                "pan2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ],
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon4",
                                children=[
                                    dcc.Graph(
                                        id="events-progressive-passes",
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawline",
                                                "drawopenpath",
                                                "drawcircle",
                                                "drawrect",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines",
                                                "pan2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ],
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
            ],
            className="g-0",  # Remover espaçamento entre colunas se necessário
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon5",
                                children=[
                                    dcc.Graph(
                                        id="events-crosses",
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawline",
                                                "drawopenpath",
                                                "drawcircle",
                                                "drawrect",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines"
                                            ],
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Card(
                        children=[
                            dcc.Loading(
                                id="loading-icon6",
                                children=[
                                    dcc.Graph(
                                        id="events-set-plays",
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawline",
                                                "drawopenpath",
                                                "drawcircle",
                                                "drawrect",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toggleSpikelines",
                                                "pan2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ],
                                        },
                                    )
                                ],
                                type="default",
                            )
                        ]
                    ),
                ),
            ],
            className="g-0",  # Remover espaçamento entre colunas se necessário
        ),
        html.Br(),
      ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
