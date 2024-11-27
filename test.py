#%%
import pandas as pd

#%%
date_filters = pd.read_csv('data-raw/date_filters.csv')

#%%
# initial filters
yr_filters = date_filters.year.drop_duplicates(ignore_index=True)
# %%
print(yr_filters)
# %%
yr_filters1 = yr_filters.sort_values(ascending=False, ignore_index=True)
# %%
yr_filters1
# %%
print(date_filters)

# %%
