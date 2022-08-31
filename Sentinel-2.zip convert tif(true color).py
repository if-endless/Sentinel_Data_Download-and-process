'''
@version: Anaconda
@author: 吃口白日梦
@contact: 460958592@qq.com
@software: PyCharm
@file: Sentinel-2.zip convert tif(true color)
@time: 2022/7/11 凌晨 00:03

'''
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import os
import pathlib
# 受postgis影响，重新设置环境变量
# os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'
# os.environ['PROJ_LIB'] = r'D:\anaconda3\envs\pytorch_GPU\Lib\site-packages\pyproj\proj_dir\share\proj'
# os.environ['GDAL_DATA'] = r'D:\anaconda3\envs\pytorch_GPU\Library\share'


# 读取栅格
def Sentinel2(path):
    # 获取文件夹的所有后缀为.zip的文件
    Rasters = list(pathlib.Path(path).glob('*.zip'))
    # 遍历这些文件
    for var in tqdm(range(0,len(Rasters))):
        # 拼接路径
        filename = os.path.join(path, Rasters[var])
        # print(filename)
        # 打开栅格文件
        root_ds = gdal.Open(filename)
        # 獲取柵格子數據集
        ds_list = root_ds.GetSubDatasets()

        # 返回结果是一个list，list中的每个元素是一个tuple，每个tuple中包含了对数据集的路径，元数据等的描述信息
        # tuple中的第一个元素描述的是数据子集的全路径
        # 取出列表元组的数据（取出真彩色）
        sub = gdal.Open(ds_list[3][0])
        # 按块读取栅格(将数据转为ndarray)
        sub_arr = sub.ReadAsArray()
        # 栅格图像的c、h、w
        dimen = np.array(sub_arr).shape
        # print(dimen)
        # print(f'打开数据为：{ds_list[3][0]}')
        # print(f'投影信息：{sub.GetProjection()}')
        # print(f'栅格波段数：{sub.RasterCount}')
        # print(f'栅格列数（宽度）：{sub.RasterXSize}')
        # print(f'栅格行数（高度）：{sub.RasterYSize}')
        # 创建.tif文件
        band_count = sub.RasterCount  # 波段数
        # print(band_count)
        bands = sub.GetRasterBand(1)
        t4 = bands.DataType
        xsize = sub.RasterXSize  # 栅格w
        ysize = sub.RasterYSize  # 栅格h
        out_tif_name = filename.split(".zip")[0] + ".tif"# # 输出格式
        # 判断文件是否存在,存在则跳出本次循环
        if os.path.isfile(out_tif_name) == True:
            print(f'{out_tif_name}文件已存在')
            continue
        #驱动器
        driver = gdal.GetDriverByName("GTiff")
        out_tif = driver.Create(out_tif_name, xsize, ysize, band_count,bands.DataType)
        out_tif.SetProjection(sub.GetProjection())  # 设置投影坐标
        out_tif.SetGeoTransform(sub.GetGeoTransform())#地理坐标变换

        # 遍历索引及波段
        for index, band in enumerate(sub_arr):
            band = np.array([band])
            # print(band)
            for i in range(len(band[:])):
                # 数据写出
                out_tif.GetRasterBand(index + 1).WriteArray(band[i])  # 将每个波段的数据写入内存
        out_tif.FlushCache()  # 写入硬盘
        out_tif = None  # 关闭tif文件


if __name__ == "__main__":
    path = r'G:\测试'
    Sentinel2(path)
    print('转换格式已完成！！！')