from datetime import datetime

import numpy as np
import pandas as pd
import dash
from dash import dcc, html, dash_table

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager

# commented out due to deployment
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)


bs_all = pd.read_csv('data-raw/balance_sheet_model.csv')

# select only relevant columns
columns_to_show = ['year', 'quarter_name', 'month_name', 'month', 'bs_flag', 'category', 'ns_bs_flag', 'ns_category', 'account_name', 'std_amount_gbp']

bs_all= bs_all[columns_to_show]
date_filters = pd.read_csv('data-raw/date_filters.csv')

bs_all['BS_Flag'] = np.where(bs_all['bs_flag']=='Assets', 'Assets', 'Liabilities and Equity')
bs_all['NS_BS_Flag'] = np.where(bs_all['ns_bs_flag']=='Assets', 'Assets', 'Liabilities and Equity')

# helper functions
def try_loc(df, column, values_to_search:list):
    if values_to_search:
        return df.loc[df[column].isin(values_to_search)]
    else:
        return df

def sort_val(df, by:list):
    return df.sort_values(by=['year', 'quarter_name', 'month'])

# new function because df.pivot does not have the aggfunc
def pivot_val(df, values:list, index:list, columns:list, aggfunc:str):
    try:
        return pd.pivot_table(df, values, index, columns, aggfunc)
    except Exception as error:
        print('Error producing pivot table: ' + repr(error))

# initial filters
yr_filters = date_filters.year.drop_duplicates().sort_values(ascending=False, ignore_index=True)

yr_initial_select = yr_filters[0]

qtr_filters = date_filters.quarter_name.drop_duplicates().sort_values(ascending=False, ignore_index=True)

bs_initial = bs_all.loc[bs_all.year == yr_initial_select
                ].pipe(pivot_val, values=['std_amount_gbp'], index=['BS_Flag', 'category'],
                columns=['year', 'quarter_name', 'month_name'], aggfunc='sum'
                ).reset_index(drop=False)

# commented out due to deployment
app = dash.Dash(__name__, long_callback_manager=long_callback_manager)
# app = dash.Dash(__name__)

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
                    children="Per Adjusted",
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
                    id="filter-month",
                    className="chk-month",
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
                id='pivot-bs',
                columns=[{"name": i, "id": i} 
                         for i in bs_initial.columns],
                data=bs_initial.to_dict('records'),
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor="paleturquoise"),
                style_data=dict(backgroundColor="lavender")
            ), 
        ),
    ]
)

@app.callback(
    Output('filter-month', 'options'), 
    Input('filter-yr', 'value'),
    Input('filter-qtr', 'value'))
def update_months(y, q):
    stripped_dates = date_filters.pipe(try_loc, "year", y
                    ).pipe(try_loc, "quarter_name", q)
    
    available_months = stripped_dates.sort_values(by='month'
                            ).month_name.drop_duplicates(ignore_index=True)
    
    return [{"label": month, "value": month} for month
                                in available_months]

# good enough for update - long callbacks are difficult
@app.callback(
    Output('pivot-bs', 'columns'),
    Output('pivot-bs', 'data'),
    Output('text-notif', 'children'),
    State('filter-yr', 'value'),
    State('filter-qtr', 'value'),
    State('filter-month', 'value'),
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
    bs_update = bs_all.pipe(try_loc, "year", y
                ).pipe(try_loc, "quarter_name", q
                ).pipe(try_loc, "month_name", m
                ).pipe(sort_val, by=['year', 'quarter_name', 'month'])

    # pd.pivot_table is different from df.pivot
    bs_pivot = bs_update.pipe(pivot_val, values=['std_amount_gbp'], index=['BS_Flag', 'category'],
                columns=['year', 'quarter_name', 'month_name'], aggfunc='sum'
                ).reset_index(drop=False)

    columns=[{"name": i, "id": i} 
                         for i in bs_pivot.columns]
    
    data = bs_pivot.to_dict('records')
    update_str = "Updated on " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    return columns, data, update_str
    

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)