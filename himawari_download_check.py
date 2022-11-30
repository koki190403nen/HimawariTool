# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import glob
import datetime

# %%
def himawari_download_check(dir_path):
    """ダウンロードしたファイルを確認する

    Args:
        dir_path (str): ダウンロードしたファイルが入っているディレクトリ

    Returns:
        (pandas.DataFrame): サマリ
    """
    file_ls = glob.glob(f'{dir_path}/*.tif')
    check_df = pd.DataFrame({'path':file_ls})
    split_df = check_df['path'].str.split('_', expand=True)
    datestr_df = split_df.iloc[:,-5]+split_df.iloc[:,-4]
    JSTdate_df = pd.to_datetime(pd.to_datetime(datestr_df).values) + datetime.timedelta(hours=9)
    days = JSTdate_df.year.astype(str) + '/' + JSTdate_df.month.astype(str) + '/' + JSTdate_df.day.astype(str)

    days_df = pd.DataFrame({'Date(JST)':days})
    summary= days_df.groupby('Date(JST)').size()
    return summary
# %%
if __name__=='__main__':
    date = himawari_download_check('T:/Uda/Himawari_tif/')
    date