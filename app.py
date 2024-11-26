import dash
from dash import Dash, dcc, html, dash_table

from dash.dependencies import Output, Input
import pandas as pd

bs_all = pd.read_csv('data-raw/balance_sheet_model.csv')
bs_all = bs_all[bs_all['year'].isin([2022, 2023, 2024])]

app = Dash(__name__)

app.layout = html.Div(
    id="app-container",
    children=[
        html.Div(
            id="header-area",
            children=[
                html.H1(
                    id="header-title",
                    children="Balance Sheet",

                ),
                html.P(
                    id="header-description",
                    children="Per Accounting Adjustment",
                ),
            ],
        ),
        html.Div(
            id="menu-area",
            children=[
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title",
                            children="Year"
                        ),
                        dcc.Checklist(
                            id="yr-filter",
                            className="yr-chk",
                            options=[{"label": year, "value": year} for year 
                                     in bs_all.year.drop_duplicates().sort_values(ascending=False)],
                            # value=bs_all.year.drop_duplicates().sort_values()[-1]
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title",
                            children="Quarter"
                        ),

                        # to use unique() does not have sort_values()
                        # sort does
                        dcc.Checklist(
                            id="qtr-filter",
                            className="qtr-chk",
                            options=[{"label": quarter, "value": quarter} for quarter
                                     in bs_all.quarter.drop_duplicates().sort_values()]
                        )
                    ]
                )
            ]
        ),
        html.Div(
            dash_table.DataTable(
                id='bs-table',
                columns=[{"name": i, "id": i} 
                         for i in bs_all.columns],
                data=bs_all.to_dict('records'),
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor="paleturquoise"),
                style_data=dict(backgroundColor="lavender")
            ), 
        ),
    ]
)

@app.callback(
    Output('header-description', 'children'), 
    Input('bs-table', 'active_cell'))
    
def update_graphs(active_cell):
    if active_cell:
        cell_data = bs_all.iloc[active_cell['row']][active_cell['column_id']]
        return f"Data: \"{cell_data}\" from table cell: {active_cell}"
    return "Click the table"

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)