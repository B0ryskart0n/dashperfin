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
    if month == 12:
        min_date = np.datetime64(f"{year}-12-01")
        max_date = np.datetime64(f"{year+1}-01-01")
    else:
        min_date = np.datetime64(f"{year}-{month:02d}-01")
        max_date = np.datetime64(f"{year}-{month+1:02d}-01")

    # Shadowing global df with local (filtered) df
    filtered_df = df.loc[
        (min_date <= df["termin"]) & (df["termin"] < max_date), :
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
def update_table(data):
    if len(data) == 0:
        return []
    else:
        # TODO Might be slow, could be optimised.
        return pd.DataFrame.from_records(data)[column_ids].to_dict("records")


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


df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")
df["data"] = df["termin"].dt.strftime("%Y-%m-%d")
df["rok"] = df["termin"].dt.year
df["miesiac"] = df["termin"].dt.month

column_ids = ["konto", "data", "kwota", "kategoria", "komentarz"]
column_names = column_ids
column_types = ["text", "datetime", "numeric", "text", "text"]
# TODO Maybe displaying datetime as date can be handled here instead of creating a new column.
column_formats = [{}, {}, {"specifier": ".2f"}, {}, {}]

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

# TODO Wyświetlanie całej kwoty
