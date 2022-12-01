#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# download_unzip_clip.py: 指定した日付・バンドのデータをダウンロード・解凍・クリッピングする


# %%
if __name__=='__main__':
    from nc2cliparr import nc2cliparr
    from arr2tif import arr2tif
else:
    from .nc2cliparr import nc2cliparr
    from .arr2tif import arr2tif

import glob
from osgeo import gdal
import numpy as np
import os
import datetime
import ftplib
import bz2
import shutil

# ftpサーバー最下層のディレクトリ内のファイルに対しバッチ処理
class DownloadUnzipClip:
    def __init__(self):
        # メタ情報
        # clipしたい範囲を座標で指定
        # 関東平野周辺の場合、広めにとると(lat_min=33.5, lat_max=38.5, lon_min=137, lon_max=142)
        self.lat_min=33.5 # 緯度min
        self.lat_max=38.5 # 緯度max
        self.lon_min=137 # 経度min
        self.lon_max=142 # 経度max

        self.ftp_user= 'meguyama'  # FTPユーザー名
        self.ftp_pass= 'hWzL92BM'  # FTPパスワード
        self.ftp_address = 'sc-trans.nict.go.jp'  # FTPアドレス

        self.HIMAWARI_Num = 8  # ひまわり何号機を使うか指定

        self.working_dir_path = None  # ワーキングディレクトリのパス

    def download_unzip_clip(self, date, band, out_dir_path, working_dir_path='./working/'):
        """指定した日付・バンドのデータをダウンロード・解凍・クリッピングする

        Args:
            date (datetime.datetime): 指定日時(UTC)
            band (int): 指定バンド
            out_dir_path (str): 出力先ディレクトリ

        Returns:
            int: 実行ファイル数
        """
        self.working_dir_path = working_dir_path


        self._himawari_download_fromFTP(date, band)  # FTPサーバーからNC2ファイルをダウンロード
        self._bunzip()

        # クリップを行う
        before_clip_ls = glob.glob(f'{self.working_dir_path}/*.nc')  # working dir内のncファイルリストを取得
        for c, before_clip_file_path in enumerate(before_clip_ls):
            get_dir_path = before_clip_file_path.split('\\')[0]                   #
            get_file_name = before_clip_file_path.split('\\')[1]                 #
            input_file_path = f'{get_dir_path}/{get_file_name}'    # 入力ファイル名再構築
            ###################################
            # 出力したいファイル名
            out_file_name = 'clip01_' + input_file_path.split('/')[-1].split('.')[0] + '.tif'
            # arr2tifで必要な値をnc2cliparrから求める(nc -> ndarray)
            clip_img, geotrans = nc2cliparr(
                input_file_path=input_file_path,
                lat_min=self.lat_min, lat_max=self.lat_max, lon_min=self.lon_min, lon_max=self.lon_max
                )

            # clipしたい範囲の配列をtifに変換して保存(ndarray -> geotiff)
            arr2tif(
                arr=clip_img,
                out_file_path=f'{out_dir_path}/{out_file_name}',
                geotrans=geotrans, projection=4326
                )
            os.remove(before_clip_file_path)  # クリップが終わったらファイルを削除
        return c+1  # 実行ファイル数を返す

    def _himawari_download_fromFTP(self, date, band):

        """FTPサーバーからひまわりデータ(.nc2)をダウンロードする

        Args:
            date (datetime.datetime): ダウンロードしたい日付(UTC)
            band (int): ダウンロードしたいバンド
            working_dir_path (str, (path))): ワーキングディレクトリ. Defaults to './working/'.
            ftp_user (str): FTPユーザ名. Defaults to 'meguyama'.
            ftp_pass (str): FTPパスワード. Defaults to 'hWzL92BM'.
            ftp_address (str,): FTPアドレス Defaults to 'sc-trans.nict.go.jp'.
        """

        os.makedirs(self.working_dir_path, exist_ok=True)
        # ftp接続
        ftp = ftplib.FTP(self.ftp_address, timeout=30)
        ftp.set_pasv('true')
        ftp.login(self.ftp_user, self.ftp_pass)

        # ftpサーバー内ディレクトリ名を構築
        nict_dir_datepath = date.strftime('/%Y%m/%d/%Y%m%d%H00/%M/')

        Bbb = f'B{str(band).zfill(2)}'

        
        ftp_dir_name= f'/himawari_real/HIMAWARI-{self.HIMAWARI_Num}/HINC/Ncjp/{nict_dir_datepath}/{Bbb}/'  # 最下層のディレクトリ名を構築

        ftp_ls = ftp.nlst(ftp_dir_name)  # ftp内ファイルのpathリストを作成

        # ftp_ls内のファイルをひとつづつ out_dir_path内にダウンロード
        for ftp_file_path in ftp_ls:
            out_file_name = ftp_file_path.split('/')[-1]
            # 空白のバイナリファイルを作成し開いて、ダウンロードデータを書き込む
            with open(f'{self.working_dir_path}/{out_file_name}', 'wb') as ftp_fb:
                ftp.retrbinary(f'RETR {ftp_file_path}', ftp_fb.write)
        ftp.close()

    def _bunzip(self):
        """ワーキングディレクトリ内のファイルを解凍(bunzip)する.
        """
        bzip_file_ls  = glob.glob(f'{self.working_dir_path}*.bz2')

        # workingディレクトリ内の物をひとつづつ解凍
        for bzip_file_path in bzip_file_ls:
            out_file_path = bzip_file_path[:-4]

            with bz2.BZ2File(bzip_file_path) as fr:
                with open(out_file_path,"wb") as fw:
                    shutil.copyfileobj(fr,fw)  # 解凍する
            os.remove(bzip_file_path)  # 最後に解凍前ファイルは消す

# %%
if __name__=='__main__':
    duc = DownloadUnzipClip()
    duc.download_unzip_clip(datetime.datetime(2020, 12, 1, 12, 0), band=1, out_dir_path='../sample_res/', working_dir_path='../working_log/')
# %%
