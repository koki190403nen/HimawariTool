# %%
from .Himawari_download import himawari_download
from .Bunzip import bunzip
from .nc2cliparr import nc2cliparr
from .arr2tif import arr2tif
import glob
from osgeo import gdal
import numpy as np
import os
import datetime

# ftpサーバー最下層のディレクトリ内のファイルに対しバッチ処理
def download_unzip_clip(date, band, out_dir_path, working_dir_path='./working/'):

    # メタ情報
    # clipしたい範囲を座標で指定
    # 関東平野周辺の場合、広めにとると(lat_min=33.5, lat_max=38.5, lon_min=137, lon_max=142)
    lat_min=33.5 # 緯度min
    lat_max=38.5 # 緯度max
    lon_min=137 # 経度min
    lon_max=142 # 経度max

    year=date.year
    month=date.month
    day=date.day
    hour=date.hour
    minute=date.minute
    
    himawari_download(
        year, month, day, hour, minute, band,
        working_dir_path
    )
    
    bunzip(working_dir_path)

    # クリップを行う
    before_clip_ls = glob.glob(f'{working_dir_path}/*.nc')  # working dir内のncファイルリストを取得
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
            lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max
            )

        # clipしたい範囲の配列をtifに変換して保存(ndarray -> geotiff)
        arr2tif(
            arr=clip_img,
            out_dir_path=out_dir_path, out_file_name=out_file_name,
            geotrans=geotrans, dtype=gdal.GDT_Float32, epsg=4326
            )
        os.remove(before_clip_file_path)  # クリップが終わったらファイルを削除
    return c+1  # 実行ファイル数を返す
