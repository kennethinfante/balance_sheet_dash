import pandas as pd

# code for piping
def try_loc(df, column, values_to_search: list):
    if values_to_search:
        return df.loc[df[column].isin(values_to_search)]
    else:
        return df

# new function because df.pivot does not have the aggfunc
def pivot_val(
    df, values: list, index: list, columns: list, aggfunc: str, margins: bool = False
):
    try:
        return pd.pivot_table(df, values, index, columns, aggfunc, margins)
    except Exception as error:
        print("Error producing pivot table: " + repr(error))


def flatten_columns(df):
    return [
        "_".join([str(c) for c in c_list if c not in ("", "std_amount_gbp")])
        for c_list in df.columns.values
    ]
