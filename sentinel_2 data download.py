# -*- coding: utf-8 -*-
'''
@author: LongChaohuo
@contact: 460958592@qq.com
@software: PyCharm
@file: Sentinel2_Download
@time: 2022/07/12 下午 14:12

'''
# 导入相应的模块
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import time
import datetime
import os
import pathlib

# sentinel-2数据下载函数
def sentinel_2_data(user_name,user_password,sentinel_url,start_date,end_date,platformname,max_cloud):
    '''
    :param user_name: 哥白尼数据访问中心账号
    :param user_password:哥白尼数据访问中心账号密码
    :param sentinel_url: 哥白尼数据访问中心URL
    :param start_date: 数据搜索起始时间
    :param end_date: 数据搜索结束时间
    :param platformname: 卫星（sentinel卫星）
    :param max_cloud: 最大云量
    :param download_dir 数据下载到本地地址
    '''
    # 获取文件下全部json文件(绝对路径)
    # 兴趣区（https://geojson.io/）
    while True:
        areas = list(pathlib.Path(path).glob('*.geojson'))
        print(areas)
        #遍历json文件
        for AOI in areas:
            # 拼接路径
            filename = os.path.join(path, AOI)
            print(f'兴趣区路径为：{filename}')
            #获取兴趣区名称
            out_file = filename.split(".geojson")[0]
            print(f'输出路径为：{out_file}')
            # 根据文件名创建文件夹
            if not os.path.exists(out_file):
                os.makedirs(out_file)
            download_area = geojson_to_wkt(read_geojson(filename))
            #  设置连接sentinel数据中心的相关参数
            sentinel_API = SentinelAPI(user_name,user_password,sentinel_url)
            sentinel_products = sentinel_API.query(
                    area=download_area,#下载兴趣区域
                    date=(start_date,end_date),#时间间隔
                    platformname= platformname, #卫星
                    producttype = producttype,#数据等级
                    cloudcoverpercentage = (0, max_cloud) #云量设置
            )
            print(f'共有产品{len(sentinel_products)}个')

            #遍历查询列表的每一个数据产品
            for product in sentinel_products:
                #根据产品元数据字典
                product_dict = sentinel_API.get_product_odata(product)
                # print(product_dict)
                #获取产品id
                product_ID = product_dict['id']
                # 获取产品文件title
                product_title = product_dict['title']
                print(f'产品名称为{product_title}')
                #通过产品id查询产品
                product_info = sentinel_API.get_product_odata(product_ID)
                #获取产品的在线及离线状态信息
                product_online = product_info['Online']
                #判断产品是否在线
                if product_online: #在线
                    print(f'产品为{product_title}在线')
                    #判断本地是否有完整产品
                    if not os.path.isfile(out_file + os.sep + product_title + ".zip"):
                        print(f'本地无 {product_title}.zip 的完整文件')
                        #通过产品id下载产品
                        sentinel_API.download(product_ID,directory_path= out_file)
                else:#产品不在线
                    print(f'产品为{product_title}不在线')
                    # 判断本地是否有完整产品
                    if not os.path.isfile(out_file + os.sep + product_title + ".zip"):
                        print(f'本地无{product_title}.zip 的完整文件，尝试触发 LongTermArchive 库')
                        try: # 尝试触发
                            sentinel_API.download(product_info['id'], directory_path= out_file)
                            sentinel_API.trigger_offline_retrieval(product_ID)
                            break  #成功则跳出
                        except Exception as e:
                            print(f'[错误]请求失败,休眠 15分钟后重试（当前时间：{datetime.datetime.now()}')
            # 每隔15min才能提交一次请求
            time.sleep(60 * 15)


if __name__ == '__main__':
    # 存放数据地址
    path = r'C:\Users\1\Desktop\思维导图\脚本（杂）\哨兵数据下载\research area'#必须是绝对路径，相对路径会出错
    # 账号及密码
    user_name="longchaohuo6"
    user_password = "5720389a"
    # 哥白尼数据访问URL
    sentinel_url = 'https://scihub.copernicus.eu/dhus'
    # 时间间隔
    start_date ='20210628'
    end_date ='20210728'
    # 下载Sentinel卫星
    platformname = 'Sentinel-2'
    # 数据类型
    producttype = 'S2MSI2A'#可选: S2MSI2A,S2MSI1C, S2MS2Ap
    #云量最大值
    max_cloud = 100
    sentinel_2_data(user_name, user_password, sentinel_url, start_date, end_date, platformname, max_cloud,
                      )

