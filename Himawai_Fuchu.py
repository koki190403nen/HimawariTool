# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime
from . import *
from .download_unzip_clip import DownloadUnzipClip
import glob
import os

# %%
class HimawariFuchuDownload:
    def __init__(self, out_dir_path, working_dir_path='./working/', log_path='./log.txt', Himawari_num=8):
        """府中のひまわりデータをダウンロードする

        Args:
            out_dir_path (str): 出力先ディレクトリ
            working_dir_path (str, optional): workingディレクトリ. Defaults to './working/'.
            log_path (str, path): 出力ログパス. Defaults to './log.txt'
            Himawari_num (int): ひまわり○号機. Defaults to 8.
        """
        self.out_dir_path = out_dir_path
        self.working_dir_path = working_dir_path
        self.log_path = log_path
        self.download_hour_ls = None  # ダウンロードするhourのリスト
        self.band_ls = None  # ダウンロードするバンドのリスト
        self.now_date = None
        self.Himawari_num = Himawari_num  # ひまわり○号機
    
    def _clean_working_dir(self):
        # 作業用ディレクトリをクリーニング
        working_file_ls = glob.glob(f'{self.working_dir_path}/*')
        for working_file_path in working_file_ls:
            os.remove(working_file_path)
    def _get_now_time(self):
        """現在の時刻を取得
        """
        self.now_date = datetime.datetime.now()


    def download_1day(self, date, download_hour_ls=range(0, 23+1), download_band_ls=range(7, 16+1)):
        """1日分をダウンロードする

        Args:
            date (datetime.datetime): ダウンロードしたい日付
            download_hour_ls (list, int): ダウンロードを実施するhour(JST)を設定
            download_band_ls (Array like, optional): ダウンロードしたいバンド. Defaults to range(7, 16+1).
        """
    
        end_date = date + datetime.timedelta(days=1)
        self.download_manydays(start=date, end=end_date, download_hour_ls=download_hour_ls, download_band_ls=download_band_ls)
        return self

    def download_manydays(self, start, end, download_hour_ls=range(0, 23+1), download_band_ls=range(1, 16+1)):
        """連続する複数の日のデータをダウンロードする.

        Args:
            start (datetime.datetime): ダウンロード開始日時(JST)
            end (datetime.datetime): ダウンロード終了日時(JST)
            download_hour_ls (Array like, optional): ダウンロードするhourのリスト. Defaults to range(0, 23).
            download_band_ls (Array like, optional): ダウンロードしたいバンド. Defaults to range(7, 16+1).

        """
        self.band_ls = download_band_ls
        self.download_hour_ls = download_hour_ls
        hour_ls = [i for i in self.download_hour_ls]
        # ダウンロードする日付の10分間隔の日付をリスト化
        download_date_ls = \
            pd.to_datetime(np.arange(start, end, datetime.timedelta(minutes=10)))
        duc = DownloadUnzipClip(Himawari_num=self.Himawari_num)

        for download_dateJST in download_date_ls:
            if download_dateJST.hour not in hour_ls:
                continue
            download_dateGMT = download_dateJST - datetime.timedelta(hours=9)  # JSTをGMTに変換

            count=0
            for band in self.band_ls:
                self._clean_working_dir()  # workingディレクトリをクリーニング
                
                try:
                    c = duc.download_unzip_clip(download_dateGMT, band, self.out_dir_path, self.working_dir_path)  # 指定バンド,指定日時のデータをダウンロード
                    count+=c
                except:
                    with open(self.log_path, 'a') as f:
                        f.write(f'{download_dateJST.strftime("%Y/%m/%d-%H:%M")}\r\n')
                    continue



            if (download_dateJST.minute==0):
                print('---')
            self._get_now_time()
            print(f'Download file:{count}, date(JST):{download_dateJST.strftime("%Y/%m/%d-%H:%M")} | (Now:{self.now_date.strftime("%Y/%m/%d %H:%M")})')
        return self
    
    def make_fb_date_ls(self, csv_path, actually_download_df_path='./act_download.csv'):
        """前後1日を含めた日付のリストを作る

        Args:
            csv_path (str): targetとなる日付の入ったcsvファイルのパス
            actually_download_df_path (str, optional): 実際にダウンロードする日付の一覧をcsvで吐き出す. Defaults to './act_download.csv'.

        Returns:
            _type_: _description_
        """
        download_date_ls_df = pd.read_csv(csv_path)
        download_date_ls = pd.to_datetime(download_date_ls_df.iloc[:,0].values)
        f_date_ls = download_date_ls - datetime.timedelta(days=1)
        b_date_ls = download_date_ls + datetime.timedelta(days=1)
        all_date_ls = list(set(list(download_date_ls)+list(f_date_ls)+list(b_date_ls)))
        all_date_ls.sort()
        all_date_arr = pd.to_datetime(all_date_ls)
        pd.DataFrame(
            {'download_date': all_date_arr}).to_csv(actually_download_df_path, index=None)
        return all_date_arr
    

    def download_from_csv(self, target_csv_path, download_hour_ls=range(0, 23+1), download_band_ls=range(7, 16+1)):
        """csvファイルから読み出した日付のデータをダウンロードする.

        Args:
            target_csv_path (_type_): ターゲットとなる日付の入ったcsvのパス
            download_hour_ls (Array like, optional): ダウンロードするhourのリスト. Defaults to range(0, 23).
            download_band_ls (Array like, optional): ダウンロードしたいバンド. Defaults to range(7, 16+1).
            

        """
        
        download_date_arr = self.make_fb_date_ls(target_csv_path)
        for date in download_date_arr:
            self.download_1day(
                date=date, 
                download_hour_ls=download_hour_ls,
                download_band_ls=download_band_ls)

        return self
    
    def download_from_log(self, log_path, download_hour_ls=range(0, 23+1), download_band_ls=range(1, 16+1)):
        """ログファイルから失敗したファイルを再ダウンロードする.

        Args:
            log_path (str): ログファイルのパス
            download_hour_ls (Array like, optional): ダウンロードするhourのリスト. Defaults to range(0, 23).
            download_band_ls (Array like, optional): ダウンロードしたいバンド. Defaults to range(1, 16+1).
        """
        print(f'start re-download from {log_path}')
        failed_ls = list(set(list(pd.read_table(log_path, header=None).iloc[:,0].values)))
        failed_ls.sort()
        print(f'start from {log_path}. Total {len(failed_ls)} baches')
        for failed_path in failed_ls:
            date = datetime.datetime.strptime(failed_path, '%Y/%m/%d-%H:%M')
            self.download_manydays(
                start=date, end=date+datetime.timedelta(minutes=10),
                download_hour_ls=download_hour_ls,
                download_band_ls=download_band_ls
            )
        print('Complete')



# %%
if __name__=='__main__':
    hfd = HimawariFuchuDownload(out_dir_path='./download/', working_dir_path='./working/')
    hfd.download_from_csv('./download_date_ls.csv')
