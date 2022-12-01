# ndarray -> geotiffに変換して保存する関数
# %%
from osgeo import gdal, ogr, osr, gdal_array
import numpy as np

# %%
# %%
def arr2tif(
    arr:np.ndarray,
    out_file_path,
    geotrans, projection=4326,
    ):
    """np.ndarrayをgeotiff形式で保存

    Args:
        arr (np.ndarray): データセット本体
        out_file_path (str): 出力ファイルパス
        geotrans (set(lon, Δlon, 0, lat, 0, -Δlat)): 左上ピクセルの座標情報
        projection (int or str): 座標系.int型ならEPSGコード,strならWktコード. Defaults to 4326.
    """

    cols, rows = arr.shape[1], arr.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    gdal_type = gdal_array.NumericTypeCodeToGDALTypeCode(arr.dtype)  # numpy.dtype をgdal.DataTypeに変換
    outRaster = driver.Create(out_file_path, cols, rows, 1, gdal_type)
    outRaster.SetGeoTransform(geotrans)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(arr)

    # projectionがEPSGコードだった場合の処理
    if type(projection) is int:
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(projection)
        projection = outRasterSRS.ExportToWkt()
    outRaster.SetProjection(projection)
    outband.FlushCache()
    del outRaster