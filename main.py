import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dash_table, dcc, Input, Output, callback

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

    return df.loc[(min_date <= df["termin"]) & (df["termin"] < max_date), :].copy()


@callback(
    Output("graph", "figure"),
    Output("table", "data"),
    Output("table", "columns"),
    Input("year_selection", "value"),
    Input("month_selection", "value"),
)
def update_data(year, month):
    filtered_df = filter_data(df, date_filter_lookup(year, month))
    filtered_df["kategoria_suma"] = (
        filtered_df["kwota"].groupby(filtered_df["kategoria"]).transform("sum")
    )
    # Filtering by the sum of amount spent for a category makes the plotting sorted colors repeating
    filtered_df.sort_values("kategoria_suma", inplace=True)

    updated_figure = px.bar(
        filtered_df,
        x="kwota",
        y="kategoria",
        color="kategoria",
        orientation="h",
    )

    filtered_df["data"] = filtered_df["termin"].dt.strftime("%Y-%m-%d")

    column_ids = ["konto", "data", "kwota", "kategoria", "komentarz"]
    column_names = column_ids
    column_types = ["text", "datetime", "numeric", "text", "text"]
    column_formats = [{}, {}, {"specifier": ".2f"}, {}, {}]

    updated_data_columns = [
        {"id": id, "name": name, "type": type, "format": format}
        for (id, name, type, format) in zip(
            column_ids, column_names, column_types, column_formats
        )
    ]

    updated_data = filtered_df[column_ids].to_dict("records")
    return (updated_figure, updated_data, updated_data_columns)


df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")

app = Dash(title="DashPerFin")
app.layout = [
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
    dcc.Graph(figure=None, id="graph"),
    dash_table.DataTable(
        data=None,
        columns=None,
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
