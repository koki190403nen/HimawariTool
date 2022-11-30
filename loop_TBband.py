# %%
from main_single import download_unzip_clip
import datetime
import numpy as np
import os
import glob
import pandas as pd

# メタ情報
out_dir_path = 'T:/Kawai/himawaridata_tdrive/clip01_tdrive/himawari_formimura2022/'  # 出力先ディレクトリ ### 必要に応じて変更する箇所

working_dir='./working_formimura1/'  # 作業用ディレクトリ ### 基本いじらない

# 作業用ディレクトリをクリーニング
working_file_ls = glob.glob(f'{working_dir}/*')
for working_file_path in working_file_ls:
    os.remove(working_file_path)

# %%
download_date_df=pd.read_csv('./downloaddate2022_15to18.csv')
# %%
os.makedirs(out_dir_path, exist_ok= True)  # 出力用ディレクトリを作成
os.makedirs(working_dir, exist_ok=True)  # 作業用ディレクトリを作成

print(out_dir_path)
print(f'start: {datetime.datetime.now().strftime("%m/%d %H:%M:%S")}')


if __name__=='__main__':

    for date_count in np.arange(0, len(download_date_df)):
        this_year=download_date_df.loc[date_count, 'this_year']
        this_month=download_date_df.loc[date_count, 'this_month']
        this_day=download_date_df.loc[date_count, 'this_day']
        print('')
        print(f'{this_year}/{this_month}/{this_day}')
        print('')

        ###15to18
        start_date=(datetime.datetime(this_year, this_month, this_day, 0, 0, 0) - datetime.timedelta(days=2))
        start_year=start_date.year
        start_month=start_date.month
        start_day=start_date.day

        end_date=(datetime.datetime(this_year, this_month, this_day, 0, 0, 0))
        end_year=end_date.year
        end_month=end_date.month
        end_day=end_date.day

        ###

        '''
        ###12to14
        start_date=(datetime.datetime(this_year, this_month, this_day, 0, 0, 0) - datetime.timedelta(days=1))
        start_year=start_date.year
        start_month=start_date.month
        start_day=start_date.day

        end_date=(datetime.datetime(this_year, this_month, this_day, 0, 0, 0) + datetime.timedelta(days=1))
        end_year=end_date.year
        end_month=end_date.month
        end_day=end_date.day
        ###
        '''

        for year in np.arange(start_year, end_year+1):  # 年の指定
            for month in np.arange(start_month, end_month+1):  # 月の指定
                for day in np.arange(start_day, end_day+1):  # 日の指定
                    for hour in np.arange(15, 18+1):  # 時の指定(15, 18+1)or(12, 14+1)
                        for minute in np.arange(0, 50+1, 10):  # 分の指定(10分おき)
                            #print(f'{year}/{month}/{day} {hour}:{minute}')
                            
                            count=0
                            for band in np.arange(7, 16+1):  # バンドの指定(TBBバンドは7~16)
                                # 作業用ディレクトリをクリーニング
                                working_file_ls = glob.glob(f'{working_dir}/*')
                                for working_file_path in working_file_ls:
                                    os.remove(working_file_path)
                                # 繰り返し部分
                                try:
                                    c = download_unzip_clip(
                                        year, month, day, hour, minute, band,
                                        out_dir_path=out_dir_path, working_dir_path=working_dir)
                                    count += c
                                except:
                                    with open('log_formimura1.txt', 'a') as f:
                                        f.write(f'{year}/{month}/{day}-{hour}:{minute}\r\n')
                                    continue
                            # 1単位時刻ごとにログ出力
                            print(
                                    f'Complete: {datetime.datetime.now().strftime("%m/%d %H:%M:%S")}  |(file:{count} {year}-{month}-{day}-{hour}:{minute})'
                                )
                        print('')


# %%
