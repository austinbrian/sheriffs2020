import dash_core_components as dcc
import dash_html_components as html
from .dashfigs import yaxis_cols, xaxis_cols


class XDiv:
    checkbox_options = [
        {
            "label": "President",
            "value": "pres",
            "disabled": True,
        },
        {
            "label": "US Senate",
            "value": "sen",
            "disabled": False,
        },
        {
            "label": "Governor",
            "value": "gov",
            "disabled": False,
        },
        {
            "label": "Lt. Governor",
            "value": "ltgov",
            "disabled": False,
        },
        {
            "label": "Attorney General",
            "value": "ag",
            "disabled": False,
        },
    ]

    def __new__(cls):
        return html.Div(
            children=[
                html.P(
                    "Select x-axis",
                    style={"font-weight": "bold", "font-size": 16},
                ),
                dcc.RadioItems(
                    id="xaxis-column",
                    options=xaxis_cols(),
                    value="per_dem",
                    labelStyle={
                        "display": "inline-block",
                        "font-style": "bold",
                    },
                    style={
                        "padding": "5px 20px",
                        "max-width": "250px",
                        "display": "flex",
                        "justify-content": "space-between",
                    },
                    # placeholder="Dem % 2020",
                    # multi=True,
                    # style=dict(width="600px"),
                ),
                dcc.Checklist(
                    id="xaxis-checkboxes",
                    options=cls.checkbox_options,
                    value=["sen", "gov", "ltgov", "ag"],
                    # labelStyle={"display": "flex"},
                    style={
                        "padding": "5px",
                        "margin": "2%",
                        # "display": "flex",
                        # "justify-content": "space-between",
                    },
                ),
                html.P(
                    id="explain-x-axis",
                    children="",
                    style={
                        "font-style": "italic",
                        "font-size": 12,
                    },
                ),
            ],
            id="xdiv",
            style={
                "width": "49%",
                "display": "inline-block",
                "padding": "10px",
            },
        )


class YDiv:
    def __new__(cls):
        return html.Div(
            id="ydiv",
            children=[
                html.P(
                    "Select y-axis",
                    style={"font-weight": "bold", "font-size": 16},
                ),
                dcc.RadioItems(
                    id="mult_or_single_yaxis",
                    options=[
                        {"label": l, "value": v}
                        for l, v in zip(
                            ["Single Factor", "Multiple Factors"],
                            ["single", "multiple"],
                        )
                    ],
                    value="single",
                    labelStyle={
                        "display": "inline-block",
                        "font-style": "bold",
                    },
                    style={
                        "padding": "5px 20px",
                        "max-width": "300px",
                        "display": "flex",
                        "justify-content": "space-between",
                    },
                ),
                html.P(
                    id="explain-mult",
                    children="",
                    style={
                        "font-style": "italic",
                        "font-size": 12,
                    },
                ),
                dcc.Dropdown(
                    id="yaxis-column",
                    options=yaxis_cols(),
                    value="CAP Local/All",
                    multi=True,
                    # style=dict(width="35%"),
                ),
            ],
            style={
                "width": "49%",
                "display": "inline-block",
                "padding": "10px",
            },
        )
