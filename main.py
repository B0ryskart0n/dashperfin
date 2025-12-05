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
    period = pd.Period(year=year, month=month, freq="M")

    # Need to filter out pandas.Period columns since those are not JSON serializable
    filtered_df = df.loc[df["month"] == period, column_ids].copy()
    filtered_df["category_sum"] = filtered_df.groupby("kategoria")["kwota"].transform(
        "sum"
    )

    # Filtering by the sum of amount spent for a category makes the plotting sorted colors repeating
    filtered_df.sort_values("category_sum", inplace=True)

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


@callback(
    Output("series_graph", "figure"),
    Input("category_selection", "value"),
)
def update_month_graph(values):
    return px.line(
        data_frame=monthly_categories[monthly_categories["kategoria"].isin(values)],
        x="month",
        y="kwota",
        color="kategoria",
    )


# Polish columns are meant for display, while English ones should remain private.
df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")
df["dzień"] = df["termin"].dt.strftime("%Y-%m-%d")
df["day"] = df["termin"].dt.to_period(freq="D")
df["month"] = df["termin"].dt.to_period(freq="M")

column_ids = ["konto", "dzień", "kwota", "kategoria", "komentarz"]
column_names = column_ids
column_types = ["text", "datetime", "numeric", "text", "text"]
column_formats = [{}, {}, {"specifier": ".2f"}, {}, {}]

# `as_index=False` flattens the output and is the format that px expects.
monthly_categories = df.groupby(["month", "kategoria"], as_index=False).agg(
    {"kwota": "sum"}
)
monthly_categories["month"] = monthly_categories["month"].dt.to_timestamp()
categories = monthly_categories["kategoria"].unique()
categories.sort()

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
    # TODO Wyświetlanie całej kwoty
    dcc.Dropdown(
        options=categories,
        value=[],
        multi=True,
        id="category_selection",
    ),
    dcc.Graph(figure=None, id="series_graph"),
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
