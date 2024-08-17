# %%
import polars as pl


def pl_print(df):
    with pl.Config(tbl_hide_column_data_types=True):
        print(df)
