#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DownloadErrorCheck.py: ダウンロードのエラー理由を確認する
# %%
import numpy as np
from matplotlib import pyplot as plt
from ftplib import FTP
import ftplib
import datetime
import pandas as pd

# %%

# 考えられうるエラー
# ディレクトリが存在しない
# ファイルが足りない
# パーミッションエラー

class DownloadErrorCheck:
    def __init__(self, Himawari_num=8):
        """Downloadのエラー理由を確認する

        Args:
            Himawari_num (int): ひまわり何号機か? Defaults to 8.
        """
        self.ftp_user= 'meguyama'  # FTPユーザー名
        self.ftp_pass= 'hWzL92BM'  # FTPパスワード
        self.ftp_address = 'sc-trans.nict.go.jp'  # FTPアドレス
        self._connect_ftp()  # ftpへの接続

        self.date_str = None
        self.HIMAWARI_Num = Himawari_num
        self.error_log_df = pd.DataFrame()
        self.error_log_df.index.name='JST'
        self.dir_exist = 1  # ディレクトリの存在を確認する

    def _connect_ftp(self):
        """FTPサーバーへ接続する
        """
        # ftpへの接続
        self.ftp = FTP(self.ftp_address, timeout=10)
        self.ftp.set_pasv('true')
        self.ftp.login(self.ftp_user, self.ftp_pass)
    
    def _check_dir_exist(self, date:datetime.datetime, band:int):
        """ディレクトリの有無を確認する(ディレクトリ移動も行う)

        Args:
            date (datetime.datetime): 確認したい時刻(UTC)
            band (int): 確認したいバンド

        Returns:
            self
        """
        Bbb = f'B{str(band).zfill(2)}'
        check_dir_name = f'/himawari_real/HIMAWARI-{self.HIMAWARI_Num}/HINC/Ncjp/{date.strftime("/%Y%m/%d/%Y%m%d%H00/%M/")}/{Bbb}/'
        try:
            self.ftp.cwd(check_dir_name)
        except ftplib.error_perm:  # ディレクトリが見つからない場合
            self.dir_exist*=0
        return self
    
    def _get_file_info(self):
        """現在位置の階層の情報を得る

        Returns:
            list: パーミション情報をまとめる
        """
        files=[]
        self.ftp.dir(files.append)
        permission_ls=[info[1:9] for info in files]
        return permission_ls
    
    def search_from_date(self, date_JST:datetime.datetime, download_band_ls=range(1, 16+1), debug=False):
        """指定時刻, 指定バンドに対応する階層の情報をDataFrame にまとめる

        Args:
            date_JST (datetime.datetime): 調べたい時刻 (JST)
            download_band_ls (Array like): 調べたいバンドのリスト. Defaults to range(1, 16+1).
            debug (bool, optional): デバック用 Defaults to False.

        Returns:
            pandas.DataFrame: 情報をまとめたDataFrame
        """
        date_UTC = date_JST-datetime.timedelta(hours=9)
        
        permission_ls =[]
        file_cnt=0
        should_cnt=4*len([item for item in download_band_ls])
        for band in download_band_ls:
            self._check_dir_exist(date_UTC, band)

            # ディレクトリが存在しない時
            if self.dir_exist == 0:
                break
            
            get_permission_ls = self._get_file_info()
            permission_ls += get_permission_ls
            file_cnt += len(get_permission_ls)

        permission_str=''
        if self.dir_exist == 1:
            permission_ls=list(set(permission_ls))
            for per in permission_ls:
                permission_str+=f', {per}'
            permission_str = permission_str[1:]
        

        self.error_log_df.loc[date_JST.strftime('%Y/%m/%d-%H:%M'), 'Dir_exists'] = bool(self.dir_exist)
        self.error_log_df.loc[date_JST.strftime('%Y/%m/%d-%H:%M'), 'permission'] = permission_str
        self.error_log_df.loc[date_JST.strftime('%Y/%m/%d-%H:%M'), 'files (cnt/all)'] = f'{file_cnt} / {should_cnt}'
        self.error_log_df.loc[date_JST.strftime('%Y/%m/%d-%H:%M'), 'UTC'] =date_UTC.strftime('%Y/%m/%d-%H:%M')

        if debug:
            print(f'JST: {date_JST.strftime("%Y/%m/%d-%H:%M")}')
            print('')
            print(f'exists: {bool(self.dir_exist)}')
            print('')
            print(f'permission: {permission_str}')
            print('')
            print(f'files(cnt/all) {file_cnt} / {should_cnt}')
            print('')
            print('----')
        self.dir_exist=1  # 初期化
        return self.error_log_df.loc[date_JST.strftime('%Y/%m/%d-%H:%M')]
    
    def search_from_log(self, log_path:str, download_band_ls=range(1, 16+1), debug=False):
        """ログファイルの情報から検索をかける

        Args:
            log_path (str): 検索したい時刻の入ったログのパス
            download_band_ls (Array like): 調べたいバンドのリスト. Defaults to range(1, 16+1).
            debug (bool, optional): デバック用 Defaults to False.

        Returns:
            pandas.DataFrame: 情報をまとめたDataFrame
        """
        log_path_arr = pd.to_datetime(pd.read_table(log_path).iloc[:,0].values)
        date_ls = list(set(log_path_arr.values))
        date_ls.sort()
        date_arr = pd.to_datetime(date_ls)
        for date_JST in date_arr:
            self.search_from_date(date_JST, download_band_ls, debug)

        return self.error_log_df




# %%
if __name__=='__main__':
    dec = DownloadErrorCheck()
    print(dec.search_from_log('./log.txt', debug=False))