# netCDFを指定の範囲でclipしてndarrayに変換&arr2tifで必要なgeotransを求める関数
# %%
from netCDF4 import Dataset
import numpy as np
import os


# %%
def nc2cliparr(input_file_path, lat_min, lat_max, lon_min, lon_max):
    # netCDFを読み込み
    nc = Dataset(input_file_path, 'r')
    # netCDFに入っている情報の項目名を取得
    key = nc.variables.keys()
    # 使うデータの項目名を取り出す
    main_name = list(key)[2] # himawari-8の場合アルベドか輝度温度
    lat_name = list(key)[0] # 緯度
    lon_name = list(key)[1] # 経度
    # 地理情報の配列を取り出す
    lat_arr = nc[lat_name][:].data # 緯度
    lon_arr = nc[lon_name][:].data # 経度
    # 以下の緯度経度の計算で使う精度を求める
    lat_accuracy =int(np.abs(np.round(np.log10(np.abs(lat_arr[1]-lat_arr[0])))))+2  # 緯度  
    lon_accuracy =int(np.abs(np.round(np.log10(np.abs(lon_arr[1]-lon_arr[0])))))+2 # 経度
    # 1pixelの幅を求める
    delta_lat = np.round(lat_arr[1]-lat_arr[0], lat_accuracy) # 緯度(日本ならマイナスでok)
    delta_lon = np.round(lon_arr[1]-lon_arr[0], lon_accuracy) # 経度
    # clipしたい範囲のpixelが配列の中で何行目(縦)・何列目(横)かを求める
    row_min = int(np.round((lat_max-lat_arr[0])/delta_lat, 0)) #何行目から(rowとlatでmin,max表記逆だけど日本の緯度だからok)
    row_max = int(np.round((lat_min-lat_arr[0])/delta_lat, 0)) #何行目まで(rowとlatでmin,max表記逆だけど日本の緯度だからok)
    column_min = int(np.round((lon_min-lon_arr[0])/delta_lon, 0)) #何列目から
    column_max = int(np.round((lon_max-lon_arr[0])/delta_lon, 0)) #何列目まで
    # ↑↑偶数丸めになってる？から書き直したいかも
    
    ##w_px = (column_max-column_min) +1 # clipしたい範囲が横に何pixelか
    ##h_px = (row_max-row_min) +1 # clipしたい範囲が縦に何pixelか
    # clipしたい範囲の値を配列で取り出す
    clip_img = nc[main_name][row_min:row_max+1, column_min:column_max+1].data
    # clipしたい範囲の左上のpixelの左上端の座標を求める
    upperleft_upperleft_lat = np.round(lat_arr[row_min]-delta_lat/2, lat_accuracy) # 左上端緯度
    upperleft_upperleft_lon = np.round(lon_arr[column_min]-delta_lon/2, lon_accuracy) # 左上端経度
    # ↑↑偶数丸めになってる？から書き直したいかも
    
    # 配列からgeotiffに変換するときに必要な値geotransを指定
    # geotransは(左上の経度, Δ経度, 0, 左上の緯度, 0, Δ緯度->マイナスでok)
    geotrans = (
        upperleft_upperleft_lon, delta_lon, 0,
        upperleft_upperleft_lat, 0, delta_lat
        )
    nc.close() # プロセス切断
    

    return clip_img, geotrans
