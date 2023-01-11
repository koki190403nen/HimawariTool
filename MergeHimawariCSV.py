# %%
import glob
import os

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime

# %%
# 日付を追加
class MergeHimawariCSV:
    def __init__(
        self,
        daytime_dir_path, night_dir_path,
        merged_dir_path, sorted_dir_path,
        date_arr,
        band_arr=range(7, 16+1),
        station_name='Fuchu'):
        """ひまわりcsvのマージとソートを行う
        1. 「昼のみcsv」「夜のみcsv」を結合し、「全日未ソートcsv」を作成・出力する
        2. その後、「全日未ソートcsv」を整理し、「全日ソート済csv」を作成する.
        「全日ソート済csv」は、/サイズ別/年別.csv で分けられ、変数は[date(JST), date(UTC), [各バンド平均値]]となる.
        
        Args:
            daytime_dir_path (str)      : 昼のみのcsvの入ったディレクトリのパス
            night_dir_path (str)        : 夜のみのcsvの入ったディレクトリのパス
            merged_dir_path (str)       : 「全日未ソートcsv」の入ったディレクトリ
            sorted_dir_path (str)       :「全日ソート済csv」の入ったディレクトリ
            date_arr (pandas.TimeStamp) : 整理対象の日付のリスト(UTC)
            band_arr (Array like)       : 対象のバンドのイテラブルオブジェクト
            station_name (str)          : 地点名 Default to 'Fuchu'.
        """
        self.daytime_dir_path   = daytime_dir_path  # 昼のみのcsvの入ったディレクトリのパス
        self.night_dir_path     = night_dir_path    # 夜のみのcsvの入ったディレクトリのパス

        self.merged_dir_path     = merged_dir_path  # 「全日未ソートcsv」の入ったディレクトリ
        self.sorted_dir_path    = sorted_dir_path   # 「全日ソート済csv」の入ったディレクトリ
        os.makedirs(self.merged_dir_path, exist_ok=True)
        os.makedirs(self.sorted_dir_path, exist_ok=True)


        self.date_arr           = date_arr          # 対象とするdateのリスト
        self.band_arr           = band_arr          # 対象とするbandのリスト
        self.station_name       = station_name      # 地点名


        self.size_ls           = [str(size).zfill(3) for size in range(3, 27+1, 2)]
    
    def run(self):
        print('Start merging...')
        year_ls = np.unique(self.date_arr.year.values)

        for date in self.date_arr:
            for band in self.band_arr:
                self.merge_himawari_csv(date, band, self.merged_dir_path)
        
        print('Complete merging & Start sorting...')
        for size in self.size_ls:
            for year in year_ls:
                os.makedirs(f'{self.sorted_dir_path}/size{size}/', exist_ok=True)
                out_df = self.sort_himawari_csv(year, size)

                out_df.to_csv(f'{self.sorted_dir_path}/size{size}/Himawari{size}_sorted_{self.station_name}_{year}.csv')
        print('FIHISH')

    def sort_himawari_csv(self, year:int, size:str):
        out_df = pd.DataFrame()
        out_df.index.name='date_ori(UTC)'

        for band in range(7, 16+1):
            get_file_ls = glob.glob(f'{self.merged_dir_path}/Himawari_{self.station_name}_unsorted_{year}*_b{str(band).zfill(2)}.csv')
            get_mean_col_ls = []
            for get_file_path in get_file_ls:
                get_df = pd.read_csv(get_file_path, index_col=0)
                get_mean_col_ls.append(get_df[f'mean{size}'])

            out_df[f'B{str(band).zfill(2)}'] = pd.concat(get_mean_col_ls)
        
        out_df = self._fill_10minutes(out_df, year)

        out_df['date_JST'] = pd.to_datetime(out_df.index) + datetime.timedelta(hours=9, minutes=10)
        out_df = out_df[['date_JST']+[f'B{str(band).zfill(2)}' for band in range(7, 16+1)]]
        out_df.index.name='date_UTC'
        return out_df
    
    def _fill_10minutes(self, df, year):
        true_index_JST = pd.to_datetime(
            np.arange(
                datetime.datetime(year, 1, 1, 0, 0, 0),
                datetime.datetime(year, 12, 31, 23, 59),
                datetime.timedelta(minutes=10)
            )
        )
        true_index_UTC      = true_index_JST - datetime.timedelta(hours=9)

        actual_index_UTC    = pd.to_datetime(df.index)
        lack_index_UTC      = true_index_UTC[~true_index_UTC.isin(actual_index_UTC)]

        insert_df = pd.DataFrame(
            index   = lack_index_UTC,
            columns = df.columns
        )
        df.index = pd.to_datetime(df.index)
        concat_df = pd.concat([df, insert_df]).sort_index()
        return concat_df

    def _make_dateindex(self, df):
        """オリジナルのDataFrameにdatetime型のインデックスを付与する

        Args:
            df (pandas.DataFrame): インデックスを付与するDataFrame

        Returns:
            pandas.DataFrame: インデックス付与後のDataFrame
        """
        df.index = pd.to_datetime(
            df['year'].astype(int).astype(str) +'/'+
            df['month'].astype(int).astype(str) + '/' + 
            df['day'].astype(int).astype(str) + '-' + 
            df['hour'].astype(int).astype(str) + ':' + 
            df['minute'].astype(int).astype(str)
        )
        return df

    # マージ用csvファイル
    def merge_himawari_csv(self, date, band, merge_dir_path):
        """指定地域, date, バンドの「全日未ソートcsv」を作成する

        Args:
            date (datetime.datetime): 結合したい日付
            band (int): 結合したいバンド
            merge_dir_path(str): 出力先ディレクトリ

        Returns:
            _type_: _description_
        """
        target_ym = date.strftime("%Y%m")

        # データの読み込み
        try:
            df1 = pd.read_csv(f'{self.daytime_dir_path}/{target_ym}/clip01_stat_{self.station_name}_{target_ym}_B{(str(band).zfill(2))}_R10.csv', index_col=None)
            df1 = self._make_dateindex(df1)
            df1_is = True
        except(FileNotFoundError):
            df1_is=False
        
        try:
            df2 = pd.read_csv(f'{self.night_dir_path}/clip01_stat_{self.station_name}_{target_ym}_B{str(band).zfill(2)}_R10_2.csv', index_col=None)
            df2 = self._make_dateindex(df2)
            df2_is = True
        except(FileNotFoundError):
            df2_is = False

        # 片方が存在しないときの処理
        if df1_is & (not df2_is):
            df1.iloc[:,7:].to_csv(f'{merge_dir_path}/Himawari_{self.station_name}_unsorted_{date.strftime("%Y%m")}_b{str(band).zfill(2)}.csv')
            print(f'{target_ym}- band{band} Daytime Only')
            return
        elif (not df1_is) & df2_is:
            df2.iloc[:,7:].to_csv(f'{merge_dir_path}/Himawari_{self.station_name}_unsorted_{date.strftime("%Y%m")}_b{str(band).zfill(2)}.csv')
            print(f'{target_ym}- band{band} Night Only')
            return
        elif (not df1_is) & (not df2_is):
            print(f'{target_ym}- band{band} Not output')
            return
        elif df1_is & df2_is:
            print(f'{target_ym}-band{band} Both')
        

        # 新しいDataFrameの行列名を設定
        new_cols = df1.columns[7:]
        new_idx  = df1.index


        # 値の結合
        df1_values  = df1.iloc[:,7:].values
        df2_values = df2.iloc[:,7:].values
        new_values = np.where(~np.isnan(df1_values), df1_values, df2_values)

        new_df = pd.DataFrame(
            new_values, index=new_idx, columns=new_cols
        )
        new_df.to_csv(f'{merge_dir_path}/Himawari_{self.station_name}_unsorted_{date.strftime("%Y%m")}_b{str(band).zfill(2)}.csv')
        return new_df

# %%
if __name__=='__main__':
    area='Tsukuba'

    mhc = MergeHimawariCSV(
        daytime_dir_path= f'T:/Kawai/python_script_tdrive/himawari_extract_mean/results/result_{area}/',
        night_dir_path  = f'T:/Kawai/python_script_tdrive/himawari_extract_mean/results/result_{area}/mean10tif2resize_R10_2/',
        merged_dir_path = f'T:/Uda/Himawari_csv/{area}/merged/',
        sorted_dir_path = f'T:/Uda/Himawari_csv/{area}/sorted/',
        station_name    = area,
        date_arr        = pd.date_range('2019/1', '2022/12', freq='MS')

    )
    mhc.run()

