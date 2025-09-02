import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dash_table, dcc, Input, Output, callback

MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
YEARS = [2024, 2025]


@callback(
    Output("store", "data"),
    Input("year_selection", "value"),
    Input("month_selection", "value"),
)
def update_store(year, month):
    # TODO Consider switching to pd.Period
    if month == 12:
        min_date = f"{year}-12-01"
        max_date = f"{year+1}-01-01"
    else:
        min_date = f"{year}-{month:02d}-01"
        max_date = f"{year}-{month+1:02d}-01"

    filtered_df = df.loc[
        (min_date <= df["dzień"]) & (df["dzień"] < max_date),
        # Need to filter out pandas.Period columns since those are not JSON serializable
        column_ids,
    ].copy()
    filtered_df["kategoria_suma"] = (
        filtered_df["kwota"].groupby(filtered_df["kategoria"]).transform("sum")
    )

    # Filtering by the sum of amount spent for a category makes the plotting sorted colors repeating
    filtered_df.sort_values("kategoria_suma", inplace=True)

    return filtered_df.to_dict("records")


@callback(
    Output("table", "data"),
    Input("store", "data"),
)
# TODO Consider going back to updating the table.data
def update_table(data):
    return data


@callback(
    Output("month_graph", "figure"),
    Input("store", "data"),
)
def update_month_graph(data):
    if len(data) == 0:
        return None
    else:
        return px.bar(
            data_frame=pd.DataFrame.from_records(data),
            x="kwota",
            y="kategoria",
            color="kategoria",
            orientation="h",
        )


# Polish columns are meant for display, while English ones should remain private.
df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")
df["dzień"] = df["termin"].dt.strftime("%Y-%m-%d")
df["day"] = df["termin"].dt.to_period(freq="D")
df["month"] = df["termin"].dt.to_period(freq="M")

column_ids = ["konto", "dzień", "kwota", "kategoria", "komentarz"]
column_names = column_ids
column_types = ["text", "datetime", "numeric", "text", "text"]
# TODO Maybe displaying datetime as date can be handled here instead of creating a new column.
column_formats = [{}, {}, {"specifier": ".2f"}, {}, {}]

# TODO Better name
# `as_index=False` flattens the output and is the format that px expects.
data_frame = df.groupby(["month", "kategoria"], as_index=False).aggregate(
    {"kwota": "sum"}
)
data_frame["month"] = data_frame["month"].dt.to_timestamp()

series_figure = px.line(
    data_frame=data_frame,
    x="month",
    y="kwota",
    color="kategoria",
)

app = Dash(title="DashPerFin")
app.layout = [
    dcc.Store(id="store"),
    dcc.RadioItems(
        options=YEARS,
        value=YEARS[0],
        inline=True,
        id="year_selection",
    ),
    dcc.RadioItems(
        options=MONTHS,
        value=MONTHS[0],
        inline=True,
        id="month_selection",
    ),
    dcc.Graph(figure=None, id="month_graph"),
    # TODO Write a selection of kategoria for the series_figure
    dcc.Graph(figure=series_figure, id="series_graph"),
    dash_table.DataTable(
        data=None,
        columns=[
            {"id": id, "name": name, "type": type, "format": format}
            for (id, name, type, format) in zip(
                column_ids, column_names, column_types, column_formats
            )
        ],
        page_action="none",
        fill_width=False,
        filter_action="native",
        sort_action="native",
        style_cell_conditional=[{"if": {"column_type": "text"}, "textAlign": "left"}],
        id="table",
    ),
]

if __name__ == "__main__":
    app.run(debug=True)

# TODO Wyświetlanie całej kwoty
