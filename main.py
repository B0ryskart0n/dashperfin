import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import dash_table, dcc, html

MONTHS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
YEARS = ["2024", "2025"]


def date_filter_lookup(year: int, month: int):
    if (month < 1) | (month > 12):
        return (np.datetime64(), np.datetime64())
    if month < 12:
        return (
            np.datetime64(f"{year}-{month:02d}-01"),
            np.datetime64(f"{year}-{month+1:02d}-01"),
        )
    else:
        return (
            np.datetime64(f"{year}-{month}-01"),
            np.datetime64(f"{year+1}-01-01"),
        )


date_filter = date_filter_lookup(2025, 6)

# TODO Make sure the format is agreed between spreadsheet and this.
# Make the work on the data the simplest, so that you simply save it as csv and
# the rest is handled here (data formatting, etc).
df = pd.read_excel("budzet.ods", sheet_name="dane", decimal=",")

# TODO Change icon and title of the page
app = dash.Dash()

fig = px.bar(df, x="kwota", y="kategoria", orientation="h")
fig.update_layout(
    yaxis={"categoryorder": "total descending"}, xaxis_title=None, yaxis_title=None
)
app.layout = [
    html.Div(
        [
            dcc.Dropdown(MONTHS, MONTHS[0], clearable=False, id="month_dropdown"),
            dcc.Dropdown(YEARS, YEARS[0], clearable=False, id="year_dropdown"),
        ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "center",
        },
    ),
    dcc.Graph(figure=fig),
    dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"id": i, "name": i} for i in df.columns],
        page_size=20,
        fill_width=False,
        filter_action="native",
        sort_action="native",
    ),
]

# TODO How to setup PROD instance
if __name__ == "__main__":
    app.run(debug=True)

# TODO Executable that opens terminal, runs the app redirecting to the site
