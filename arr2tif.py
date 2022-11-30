# ndarray -> geotiffに変換して保存する関数
# %%
from osgeo import gdal, ogr, osr
import numpy as np

# %%
def arr2tif(arr:np.ndarray, out_dir_path, out_file_name, geotrans, dtype=gdal.GDT_Float32, epsg=4326):
    # geotransは(左上の経度, Δ経度, 0, 左上の緯度, 0, Δ緯度->マイナス)
    cols, rows = arr.shape[1], arr.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(out_dir_path+out_file_name, cols, rows, 1, dtype)
    outRaster.SetGeoTransform(geotrans)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(arr)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(epsg)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
    del outRaster