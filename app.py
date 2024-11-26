from dash import Dash, html, Input, Output, dash_table
import pandas as pd

bs_all = pd.read_csv('data-raw/balance_sheet_model.csv')
bs_all = bs_all[bs_all['year'] == 2023]

app = Dash(__name__)


app.layout = html.Div([
    html.H1('Balance Sheet'),
    html.P(id='balance_sheet'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} 
                 for i in bs_all.columns],
        data=bs_all.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    ), 
])

@app.callback(
    Output('balance_sheet', 'children'), 
    Input('table', 'active_cell'))
    
def update_graphs(active_cell):
    if active_cell:
        cell_data = bs_all.iloc[active_cell['row']][active_cell['column_id']]
        return f"Data: \"{cell_data}\" from table cell: {active_cell}"
    return "Click the table"

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)