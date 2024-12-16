from datetime import datetime

import pandas as pd
import numpy as np

import dash
from dash import dcc, html, dash_table

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager

from shared import *
from utils import *

# commented out due to deployment
# import diskcache
# cache = diskcache.Cache("./cache")
# long_callback_manager = DiskcacheLongCallbackManager(cache)

# commented out due to deployment
# app = dash.Dash(__name__, long_callback_manager=long_callback_manager)

app = dash.Dash(__name__)

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
                    id="label-yr",
                    children="Year",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                ),
                html.P(
                    id="label-qtr",
                    children="Quarter",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                ),
                html.P(
                    id="label-month",
                    children="Month",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                )
            ]
        ),
        html.Div(
            id="menu-option",
            children=[
                dcc.Checklist(
                    id="filter-yr",
                    className="chk-yr",
                    options=[{"label": year, "value": year} for year 
                                in yr_filters],
                    value=[yr_initial_select],
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                    # value=bs_all.year.drop_duplicates().sort_values()[-1]
                ),
                dcc.Checklist(
                    id="filter-qtr",
                    className="chk-qtr",
                    options=[{"label": quarter, "value": quarter} for quarter
                                in qtr_filters],
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                ),
                dcc.Checklist(
                    id="filter-mo",
                    className="chk-mo",
                    style=({'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
                )
            ]
        ),
        html.Div(
            id="separator",
            children=[
                html.Br()
                , html.Button(id="btn-update", children=["Update Balance Sheet"])
                , html.P(id="text-notif", children=["Updated on " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")])
                , html.Br()
            ]
        ),
        html.Div(
            dash_table.DataTable(
                id='table-bs',
                columns=[{"name": i, "id": i} 
                         for i in bs_init_flat.columns],
                data=bs_init_flat.to_dict('records'),
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor="paleturquoise"),
                style_data=dict(backgroundColor="lavender")
            ), 
        ),
    ]
)


@app.callback(
    Output("filter-qtr", "options"),
    Input("filter-yr", "value")
)
def update_quarters(y):
    stripped_dates = date_filters.pipe(try_loc, "year", y)

    available_qtrs = stripped_dates.quarter_name.drop_duplicates().sort_values(
        ascending=False, ignore_index=True
    )

    return [{"label": qtr, "value": qtr} for qtr in available_qtrs]


@app.callback(
    Output('filter-mo', 'options'), 
    Input('filter-yr', 'value'),
    Input('filter-qtr', 'value'))
def update_months(y, q):
    stripped_dates = date_filters.pipe(try_loc, "year", y
                    ).pipe(try_loc, "quarter_name", q)

    available_months = stripped_dates.month_name.drop_duplicates().sort_values(
        ascending=False, ignore_index=True
    )

    return [{"label": month, "value": month} for month
                                in available_months]

# good enough for update - long callbacks are difficult
@app.callback(
    Output('table-bs', 'columns'),
    Output('table-bs', 'data'),
    Output('text-notif', 'children'),
    State('filter-yr', 'value'),
    State('filter-qtr', 'value'),
    State('filter-mo', 'value'),
    Input('btn-update', 'n_clicks'),
    prevent_initial_call=True,
    running=[(Output("btn-update", "disabled"), True, False)]
    # ,running=[
    #     (Output("btn-update", "disabled"), True, False),
    #     (
    #         Output("text-notif", "style"),
    #         {"visibility": "hidden"},
    #         {"visibility": "visible"},
    #     )
    # ]
)

def update_balance_sheet(y, q, m, n_clicks):
    print(y, q, m)
    print(n_clicks)

    # unlike Shiny for Python, the years are not string
    cols_to_pivot = []
    if y: cols_to_pivot.append('year')
    if q: cols_to_pivot.append('quarter_name')
    if m: cols_to_pivot.append('month_num_name')

    print(cols_to_pivot)
    # invalid combination of rows to pivot
    if (cols_to_pivot == []) or (cols_to_pivot == ['quarter_name', 'month_num_name']):
        return None, None, "Invalid Selection"

    bs_update = (
        bs_all.pipe(try_loc, "year", y)
        .pipe(try_loc, "quarter_name", q)
        .pipe(try_loc, "month_name", m)
        .sort_values(by=["year", "quarter_name", "month_num_name"])
    )

    # print("Fuck1", bs_update)
    # pd.pivot_table is different from df.pivot
    bs_pivot = bs_update.pipe(pivot_val, values=['std_amount_gbp'], index=['BS_Flag', 'category'],
                columns=cols_to_pivot, aggfunc='sum'
                )

    bs_flat = (
        bs_pivot.reset_index()
        .sort_values(by=["BS_Flag", "category"])
        .reset_index(drop=True)  # do not add the old index as new col
    )

    bs_flat.columns = flatten_columns(bs_flat)

    # print("Fuck2", bs_flat)

    print(bs_flat.columns)

    amount_cols = {
            k: v
            for k, v in enumerate(bs_flat.columns)
            if v not in ("BS_Flag", "category")
        }

    for col in amount_cols.values():
        bs_flat[str(col)] = bs_flat[str(col)].map("£ {:,.0f}".format)

    columns=[{"name": i, "id": i} 
                         for i in bs_flat.columns]

    data = bs_flat.to_dict('records')
    update_str = "Updated on " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    return columns, data, update_str


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
