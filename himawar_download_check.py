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
    check_df = pd.DataFrame()
    for i, file_path in enumerate(file_ls):
        date_str = file_path.split('_')[-5]+'-'+file_path.split('_')[-4]
        date = datetime.datetime.strptime(date_str, '%Y%m%d-%H%M') +datetime.timedelta(hours=9)
        check_df.loc[i, 'date'] = date
        check_df.loc[i, 'days(JST)'] = date.strftime('%Y/%m/%d')
    return check_df.groupby('days').size()
# %%
if __name__=='__main__':
    print(himawari_download_check('T:/Uda/Himawari_tif/'))