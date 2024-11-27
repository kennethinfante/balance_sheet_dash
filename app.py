import dash
from dash import Dash, dcc, html, dash_table

from dash.dependencies import Output, Input
import pandas as pd

bs_all = pd.read_csv('data-raw/balance_sheet_model.csv')

# select only relevant columns
columns_to_show = ['year', 'quarter_name', 'month_name', 'bs_flag', 'category', 'account_name', 'std_amount_gbp']

bs_all = bs_all[columns_to_show]
date_filters = pd.read_csv('data-raw/date_filters.csv')

# initial filters
yr_filters = date_filters.year.drop_duplicates(ignore_index=True).sort_values(ascending=False, ignore_index=True)

yr_initial_select = yr_filters[0]

qtr_filters = date_filters.quarter_name.drop_duplicates().sort_values(ascending=False, ignore_index=True)

# bs_initial = bs_all[bs_all['year'] == yr_initial_select]
bs_initial = bs_all.loc[bs_all['year'] == yr_initial_select, :]

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
            id="menu-label",
            children=[
                html.P(
                    id="yr-label",
                    children="Year",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                ),
                html.P(
                    id="qtr-label",
                    children="Quarter",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                ),
                html.P(
                    id="month-label",
                    children="Month",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                )
            ]
        ),
        html.Div(
            id="menu-option",
            children=[
                dcc.Checklist(
                    id="yr-filter",
                    className="yr-chk",
                    options=[{"label": year, "value": year} for year 
                                in yr_filters],
                    value=[yr_initial_select],
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                    # value=bs_all.year.drop_duplicates().sort_values()[-1]
                ),
                dcc.Checklist(
                    id="qtr-filter",
                    className="qtr-chk",
                    options=[{"label": quarter, "value": quarter} for quarter
                                in qtr_filters],
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                )
            ]
        ),
        html.Div(
            id="separator",
            children=[
                html.Br()
                ,html.Button("Show Balance Sheet", id="show-balance-sheet", n_clicks=0)
                , html.Hr(), html.Br()]
        ),
        html.Div(
            dash_table.DataTable(
                id='bs-table',
                columns=[{"name": i, "id": i} 
                         for i in bs_initial.columns],
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