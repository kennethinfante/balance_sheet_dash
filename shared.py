import pandas as pd
import numpy as np
from utils import *

bs_all = pd.read_csv("data-raw/balance_sheet_model.csv")
bs_all["BS_Flag"] = np.where(
    bs_all["bs_flag"] == "Assets", "Assets", "Liabilities & Equity"
)
bs_all["NS_BS_Flag"] = np.where(
    bs_all["ns_bs_flag"] == "Assets", "Assets", "Liabilities & Equity"
)
bs_all["month_num_name"] = bs_all["month"].astype("str") + bs_all["month_name"]

# select only relevant columns
columns_to_show = [
    "year",
    "quarter_name",
    "month_name",
    "month_num_name",
    "BS_Flag",
    "category",
    "account_name",
    "std_amount_gbp",
]

bs_all = bs_all[columns_to_show]
date_filters = pd.read_csv("data-raw/date_filters.csv")

# initial filters
yr_filters = date_filters.year.drop_duplicates().sort_values(
    ascending=False, ignore_index=True
)

yr_initial_select = yr_filters[0]

qtr_filters = date_filters.quarter_name.drop_duplicates().sort_values(
    ascending=False, ignore_index=True
)

# bs_initial = bs_all[bs_all['year'] == yr_initial_select]
bs_init = bs_all.loc[bs_all.year == yr_initial_select].sort_values(
    by=["year", "quarter_name", "month_num_name"]
)


bs_init_pivot = bs_init.pipe(
    pivot_val,
    values=["std_amount_gbp"],
    index=["BS_Flag", "category"],
    columns=["year", "quarter_name", "month_num_name"],
    aggfunc="sum",
)

bs_init_flat = (
    bs_init_pivot.reset_index()
    .sort_values(by=["BS_Flag", "category"])
    .reset_index(drop=True)  # do not add the old index as new col
)

bs_init_flat.columns = flatten_columns(bs_init_flat)

# print("Fuck2", bs_flat)

print(bs_init_flat.columns)

amount_cols = {
        k: v
        for k, v in enumerate(bs_init_flat.columns)
        if v not in ("BS_Flag", "category")
    }

for col in amount_cols.values():
    bs_init_flat[str(col)] = bs_init_flat[str(col)].map("£ {:,.0f}".format)
