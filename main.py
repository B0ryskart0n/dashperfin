import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, callback

MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
YEARS = [2024, 2025]


def date_filter_lookup(year: int, month: int):
    if month == 12:
        return (
            np.datetime64(f"{year}-12-01"),
            np.datetime64(f"{year+1}-01-01"),
        )
    else:
        return (
            np.datetime64(f"{year}-{month:02d}-01"),
            np.datetime64(f"{year}-{month+1:02d}-01"),
        )


def filter_data(df: pd.DataFrame, date_filter: tuple[np.datetime64, np.datetime64]):
    min_date = date_filter[0]
    max_date = date_filter[1]

    return df[(min_date <= df.termin) & (df.termin < max_date)]


df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")

app = Dash(title="DashPerFin")

app.layout = [
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    options=YEARS,
                    value=YEARS[0],
                    clearable=False,
                    id="year_dropdown",
                ),
                style={"width": "20%"},
            ),
            html.Div(
                dcc.Dropdown(
                    options=MONTHS,
                    value=MONTHS[0],
                    clearable=False,
                    id="month_dropdown",
                ),
                style={"width": "20%"},
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "center",
        },
    ),
    dcc.Graph(figure=None, id="graph"),
    dash_table.DataTable(
        data=None,
        columns=[{"id": i, "name": i} for i in df.columns],
        page_size=20,
        fill_width=False,
        filter_action="native",
        sort_action="native",
        id="table",
    ),
]


@callback(
    Output("graph", "figure"),
    Output("table", "data"),
    Input("year_dropdown", "value"),
    Input("month_dropdown", "value"),
)
def update_data(year, month):
    filtered_df = filter_data(df, date_filter_lookup(year, month))
    filtered_df["kategoria_suma"] = (
        filtered_df["kwota"].groupby(filtered_df["kategoria"]).transform("sum")
    )
    filtered_df.sort_values("kategoria_suma", inplace=True)

    updated_figure = px.bar(
        filtered_df,
        x="kwota",
        y="kategoria",
        color="kategoria",
        orientation="h",
    )

    updated_data = filtered_df.to_dict("records")
    return (updated_figure, updated_data)


if __name__ == "__main__":
    app.run(debug=True)

# TODO Executable that opens terminal, runs the app redirecting to the site
