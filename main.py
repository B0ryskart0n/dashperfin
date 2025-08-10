import pandas as pd
import dash
from dash import dash_table

# TODO Make sure the format is agreed between spreadsheet and this.
# Make the work on the data the simplest, so that you simply save it as csv and
# the rest is handled here (data formatting, etc).
# TODO Fix date format to YYYY-MM-DD
df = pd.read_csv("dane.csv")

# TODO Change icon and title of the page
app = dash.Dash()
app.layout = [
    dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"id": i, "name": i} for i in df.columns],
        page_size=20,
        fill_width=False,
        filter_action="native",
        sort_action="native",
    )
]

# TODO How to setup PROD instance
if __name__ == "__main__":
    app.run(debug=True)

# TODO Executable that opens terminal, runs the app redirecting to the site
