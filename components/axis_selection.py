import dash_core_components as dcc
import dash_html_components as html
from .dashfigs import yaxis_cols, xaxis_cols


class XDiv:
    checkbox_options = [
        {
            "label": "2020 President",
            "value": "pres",
            "disabled": False,
        },
        {
            "label": "2018 US Senate",
            "value": "sen",
            "disabled": False,
        },
        {
            "label": "2018 Governor",
            "value": "gov",
            "disabled": False,
        },
        {
            "label": "2018 Lt. Governor",
            "value": "ltgov",
            "disabled": False,
        },
        {
            "label": "2018 Attorney General",
            "value": "ag",
            "disabled": False,
        },
        {
            "label": "2018 US House",
            "value": "ushouse",
            "disabled": False,
        },
    ]

    @staticmethod
    def create_office_name_to_short_name_dict():
        sens = {i: "sen" for i in ["us senator", "senate", "us senate", "us sen"]}
        govs = {i: "gov" for i in ["gov", "governor", "gubernatorial"]}
        ltgovs = {i: "ltgov" for i in ["lt gov", "lt governor", "lieutenant governor"]}
        ags = {i: "ag" for i in ["attorney general", "ag"]}
        reps = {
            i: "ushouse" for i in ["us house", "house", "us house of representatives"]
        }
        off_dict = dict(**sens, **govs, **ags, **reps, **ltgovs)
        return off_dict

    @staticmethod
    def convert_office_names_to_short_name_list(cls, *names):
        if names:
            off_dict = cls.create_office_name_to_short_name_dict()
            cln_names = [i.lower().replace(".", "") for i in names]
            return list(
                filter(lambda x: x is not None, [off_dict.get(i) for i in cln_names])
            )
        else:
            return

    @classmethod
    def update_checkbox_items(cls, *offices):
        """expects offices in short format e.g., sen, house, ltgov"""
        chops = []
        for i in cls.checkbox_options:
            # for the moment, the 2020 presidential should always be enabled
            if i["value"] == "pres":
                i["disabled"] = False
                chops.append(i)
            elif i["value"] in offices:
                i["disabled"] = False
                chops.append(i)
            else:
                i["disabled"] = True
                chops.append(i)

        return chops

    @classmethod
    def update_checkbox_values(cls, *offices):
        return cls.convert_office_names_to_short_name_list(offices)

    def __new__(cls):
        return html.Div(
            children=[
                html.P(
                    "Select x-axis",
                    style={"font-weight": "bold", "font-size": 16},
                ),
                html.Div(
                    [
                        dcc.Checklist(
                            id="xaxis-checkboxes",
                            options=cls.checkbox_options,
                            value=["pres", "sen", "gov", "ltgov", "ag", "ushouse"],
                            # labelStyle={"display": "flex"},
                            style={
                                "padding": "5px",
                                "margin": "1%",
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
                                "max-width": "150px",
                                "font-weight": "300",
                            },
                        ),
                    ],
                    style={"display": "flex"},
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
                    style=dict(width="90%"),
                ),
            ],
            style={
                "width": "49%",
                "display": "inline-block",
                "padding": "10px",
            },
        )
