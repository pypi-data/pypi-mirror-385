#!/usr/bin/env python
# coding: utf-8
import geopandas as gpd
from shapely.ops import unary_union, triangulate,voronoi_diagram
from shapely.geometry import Polygon,Point,LineString,MultiPolygon, MultiPoint
from shapely import wkt
import pandas as pd
import numpy as np
import math,os,simplekml
import shapefile
import shutil
from geographiclib.geodesic import Geodesic
import kml2geojson as k2g
from itertools import chain
from scipy.spatial import cKDTree
import pyproj
from .utils import *
from typing import Optional


def min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=1, include_self=False) -> pd.DataFrame:
    """
    计算DataFrame中每个点的最近n个点(可选择是否包含自身)
    
    参数:
    df (DataFrame): 输入数据
    lon (str): 经度列名
    lat (str): 纬度列名
    id (str): ID列名，默认为'id'
    n (int): 要查找的最近邻数量
    include_self (bool): 是否包含自身点，默认为False
    
    返回:
    DataFrame: 添加了最近邻信息的副本
    示例：
    import pandas as pd
    import pandasgeo as pdg

    # 创建两个示例DataFrame
    df2 = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'lon2': [116.403, 116.407, 116.404, 116.408],
        'lat2': [39.914, 39.918, 39.916, 39.919]
    })

    # 计算最近的1个点
    result = pdg.min_distance_onetable(df2,'lon2','lat2',idname='id',n=1)
    print("结果示例（距离单位：米）:")
    print(result)
    print(result2)
    结果展示：
    **最近1个点**
    id	lon2	lat2	nearest1_id	nearest1_lon2	nearest1_lat2	nearest1_distance
    0	p1	114.01	30.01	p2	114.05	30.05	5881.336911
    1	p2	114.05	30.05	p1	114.01	30.01	5881.336911
    2	p3	114.12	30.12	p2	114.05	30.05	10289.545038

    """
    # 参数验证
    if n < 1:
        raise ValueError("n must be > 0")
    if lon not in df.columns or lat not in df.columns:
        raise ValueError("Longitude or latitude column not found")
    if idname not in df.columns:
        raise ValueError("ID column not found")
    if df.empty:
        return df  # 返回空 DataFrame 而不是抛出异常
    detected_crs = detect_crs(df, lon, lat)
    # 创建结果副本
    result = df.copy()
    
    # 处理空数据或数据量不足的情况
    if len(df) == 0 or (len(df) == 1 and not include_self):
        for i in range(1, n+1):
            result[f'nearest{i}_{idname}'] = np.nan
            result[f'nearest{i}_{lon}'] = np.nan
            result[f'nearest{i}_{lat}'] = np.nan
            result[f'nearest{i}_distance'] = np.nan
        if n > 1:
            result['mean_distance'] = np.nan
        return result
    
    # 提取坐标点
    points, proj_crs = create_projected_kdtree(result, lon, lat)

    # 创建KDTree
    tree = cKDTree(points)
    
    # 计算要查询的邻居数量
    # 如果不包含自身，需要额外查询1个点(因为第一个是自身)
    k_query = n + (0 if include_self else 1)
    # 确保不超过数据集大小
    k_query = min(k_query, len(df))
    
    # 查询最近的k个点
    distances, indices = tree.query(points, k=k_query, workers=-1)
    
    # 处理单个邻居的情况(确保是二维数组)
    if k_query == 1:
        distances = distances.reshape(-1, 1)
        indices = indices.reshape(-1, 1)
    
    # 如果不包含自身，跳过第一列(自身点)
    if not include_self and k_query > 1:
        distances = distances[:, 1:]
        indices = indices[:, 1:]
    
    # 确保结果有正确的列数
    current_k = distances.shape[1] if len(distances.shape) > 1 else 1
    
    # 初始化结果数组
    result_indices = np.full((len(df), n), -1, dtype=int)
    result_distances = np.full((len(df), n), np.nan)
    
    # 填充有效数据
    valid_cols = min(current_k, n)
    if valid_cols > 0:
        if len(distances.shape) == 1:
            result_indices[:, 0] = indices
            result_distances[:, 0] = distances
        else:
            result_indices[:, :valid_cols] = indices[:, :valid_cols]
            result_distances[:, :valid_cols] = distances[:, :valid_cols]
    
    # 添加最近邻信息到结果DataFrame
    for i in range(n):
        # 获取当前列的索引
        col_indices = result_indices[:, i]
        
        # 初始化列
        id_values = []
        lon_values = []
        lat_values = []
        
        # 填充数据
        for idx in col_indices:
            if idx >= 0:
                id_values.append(df.iloc[idx][idname])
                lon_values.append(df.iloc[idx][lon])
                lat_values.append(df.iloc[idx][lat])
            else:
                id_values.append(np.nan)
                lon_values.append(np.nan)
                lat_values.append(np.nan)

        result[f'nearest{i+1}_{idname}'] = id_values
        result[f'nearest{i+1}_{lon}'] = lon_values
        result[f'nearest{i+1}_{lat}'] = lat_values
        result[f'nearest{i+1}_distance'] = result_distances[:, i]

    # 添加平均距离(当n>1时)
    if n > 1:
        dist_cols = [f'nearest{j+1}_distance' for j in range(n)]
        result['mean_distance'] = result[dist_cols].mean(axis=1)

    return result


def min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2', df2_id='id', n=1,
                          crs1: Optional[str]=None, crs2: Optional[str]=None) -> pd.DataFrame:
    """
    计算df1中每个点到df2中最近的n个点的距离
    
    该函数使用KDTree算法高效计算两个DataFrame之间的最近邻距离。
    坐标系统必须一致（当前仅支持WGS84/EPSG:4326）。
    距离通过UTM投影计算，单位为米。
    
    Parameters
    ----------
    df1 : pd.DataFrame
        源数据表，包含待查询的坐标点
    df2 : pd.DataFrame
        目标数据表，包含参考坐标点
    lon1 : str, default='lon1'
        df1的经度列名
    lat1 : str, default='lat1'
        df1的纬度列名
    lon2 : str, default='lon2'
        df2的经度列名
    lat2 : str, default='lat2'
        df2的纬度列名
    df2_id : str, default='id'
        df2中用于标识点的ID列名
    n : int, default=1
        要查找的最近邻数量
    crs1 : str, optional
        df1的坐标系统，如 'EPSG:4326'。如果为None则自动检测
    crs2 : str, optional
        df2的坐标系统，如 'EPSG:4326'。如果为None则自动检测
    
    Returns
    -------
    pd.DataFrame
        返回df1的副本，添加以下列：
        - nearest{i}_{df2_id} : 第i近的点的ID
        - nearest{i}_{lon2} : 第i近的点的经度
        - nearest{i}_{lat2} : 第i近的点的纬度
        - nearest{i}_distance : 距离（米）
        - mean_distance : 前n个最近点的平均距离（当n>1时）
    
    Raises
    ------
    ValueError
        - 如果n < 1
        - 如果两个DataFrame的坐标系不一致
        - 如果坐标范围不符合WGS84标准
    
    Examples
    --------
    import pandas as pd
    df1 = pd.DataFrame({
        'id': [1, 2, 3],
        'lon1': [116.404, 116.405, 116.406],
        'lat1': [39.915, 39.916, 39.917]
    })
    df2 = pd.DataFrame({
        'id': ['A', 'B', 'C'],
        'lon2': [116.403, 116.407, 116.404],
        'lat2': [39.914, 39.918, 39.916]
    })
    # 计算df1中每个点到df2中最近的那个点
    result = pdg.min_distance_twotable(df1, df2,lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2', df2_id='id', n=1)
    print(result)
    
    Notes
    -----
    - 距离计算使用UTM投影，确保精度
    - 使用cKDTree进行高效的最近邻搜索
    - 当n大于df2的点数时，缺失的邻居会用NaN填充
    - 坐标系统必须为WGS84 (EPSG:4326)
    """
    # 验证输入
    if n < 1:
        raise ValueError("参数 n 必须大于等于 1")
    # 处理空数据情况
    if len(df2) == 0 or len(df1) == 0:
        for i in range(1, n + 1):
            df1[f'nearest{i}_{df2_id}'] = np.nan
            df1[f'nearest{i}_{lon2}'] = np.nan
            df1[f'nearest{i}_{lat2}'] = np.nan
            df1[f'nearest{i}_distance'] = np.nan
        if n > 1:
            df1['mean_distance'] = np.nan
        return df1
    # 检测或验证坐标系
    detected_crs1 = detect_crs(df1, lon1, lat1)
    detected_crs2 = detect_crs(df2, lon2, lat2)
    
    # 如果用户指定了CRS，验证是否匹配
    if crs1 is not None and crs1 != detected_crs1:
        raise ValueError(
            f"指定的 crs1={crs1} 与检测到的坐标系 {detected_crs1} 不匹配"
        )
    if crs2 is not None and crs2 != detected_crs2:
        raise ValueError(
            f"指定的 crs2={crs2} 与检测到的坐标系 {detected_crs2} 不匹配"
        )
    
    # 检查两个DataFrame的坐标系是否一致
    if detected_crs1 != detected_crs2:
        raise ValueError(
            f"两个DataFrame的坐标系不一致！\n"
            f"df1 坐标系: {detected_crs1}\n"
            f"df2 坐标系: {detected_crs2}\n"
            f"请确保两个数据集使用相同的坐标系统。"
        )
    
    # 创建结果副本
    result = df1.copy()
    
    
    # 将df1坐标投影到UTM（单位：米）
    A_points, proj_crs = create_projected_kdtree(df1, lon1, lat1)
    
    # 为df2创建转换器（使用相同的UTM投影）
    transformer_b = pyproj.Transformer.from_crs(
        "EPSG:4326", 
        proj_crs, 
        always_xy=True
    )
    lons_b = df2[lon2].values
    lats_b = df2[lat2].values
    x_b, y_b = transformer_b.transform(lons_b, lats_b)
    B_points = np.column_stack((x_b, y_b))
    
    # 创建KDTree进行高效搜索
    tree = cKDTree(B_points)
    
    # 查询最近的n个点
    k = min(n, len(df2))
    distances, indices = tree.query(A_points, k=k, workers=-1)
    
    # 处理k=1时的维度问题
    if k == 1:
        distances = distances.reshape(-1, 1)
        indices = indices.reshape(-1, 1)
    
    # 添加最近邻信息
    for i in range(k):
        nearest_points = df2.iloc[indices[:, i]]
        result[f'nearest{i+1}_{df2_id}'] = nearest_points[df2_id].values
        result[f'nearest{i+1}_{lon2}'] = nearest_points[lon2].values
        result[f'nearest{i+1}_{lat2}'] = nearest_points[lat2].values
        result[f'nearest{i+1}_distance'] = distances[:, i]  # 单位：米
    
    # 添加缺失的列（当n > k时）
    for i in range(k, n):
        result[f'nearest{i+1}_{df2_id}'] = np.nan
        result[f'nearest{i+1}_{lon2}'] = np.nan
        result[f'nearest{i+1}_{lat2}'] = np.nan
        result[f'nearest{i+1}_distance'] = np.nan
    
    # 添加平均距离（当n > 1时）
    if n > 1:
        dist_cols = [f'nearest{i+1}_distance' for i in range(min(n, k))]
        if dist_cols:
            result['mean_distance'] = result[dist_cols].mean(axis=1)
        else:
            result['mean_distance'] = np.nan
    
    return result


def add_buffer(data,lon='lon',lat='lat',distance=50):
    '''
    作用：给每个点添加一个缓冲区面
    参数说明：
    data:DataFrame - 带有经纬度两列
    lon, lat: str - 经纬度字段名
    distance：缓冲区的距离（米）
    return GeoDataFrame
    '''
    gdf = add_points(data,lon,lat)
    gdf_crs = gdf.crs
    utm_crs = gdf.estimate_utm_crs()
    gdf_buffer = gdf.to_crs(utm_crs).buffer(distance).to_crs(gdf_crs)
    gdf['geometry'] = gdf_buffer
    return gdf
def add_buffer_df(df,lon='lon',lat='lat',buff_col='distance',geometry='geometry'):
    '''
    作用：将一个经纬度数据进行扩大buffer，接受数据列为距离
    '''        
    df = df.copy()
    df[geometry]=df[[lon,lat]].apply(lambda x:Point((x[0],x[1])),axis=1)
    df=gpd.GeoDataFrame(df,crs="epsg:4326",geometry=geometry)
    df=df.to_crs(epsg=32650)
    df[geometry]=df[[geometry,buff_col]].apply(lambda x:x[0].buffer(x[1]),axis=1)
    df=df.to_crs(epsg=4326)
    return df
def add_buffer_groupbyid(data,lon='lon',lat='lat',distance=50,
                        columns_name='聚合id',id_lable_x='聚合_'):
    '''
    作用：按照给定的距离将一些点位融合在一起，添加一列聚合id用于标识
    参数说明：
    data:DataFrame - 带有经纬度两列
    lon, lat: str - 经纬度字段名
    distance：聚合的距离
    columns_name：添加的聚合的列名
    id_lable_x：添加的聚合列的内容命名前缀例如'聚合_'就会出现‘聚合_1’
    return DataFrame
    '''
    data_buffer = add_buffer(data,lon,lat,distance)
    # Use GeoDataFrame.dissolve
    data_dissolve = data_buffer[['geometry']].dissolve()
    # Explode multi-polygons to single polygons
    data_explode = data_dissolve.explode(index_parts=True).reset_index()
    print(data_explode.columns)
    data_explode[columns_name] = id_lable_x + data_explode['level_0'].astype(str)
    print(data_explode.columns)
    
    data_sjoin = gpd.sjoin(add_points(data,lon,lat),data_explode,how='left')
    
    # Ensure original columns are preserved
    print('data_sjoin::',data_sjoin.columns)
    data_columns = list(data.columns)
    print(columns_name,data_columns)
    if columns_name not in data_columns:
        data_columns.append(columns_name)
    
    # Drop extra columns from sjoin
    data_sjoin_use = data_sjoin[data_columns]
    return data_sjoin_use

def add_delaunay(
                df,
                id_use='栅格ID',
                lon='lon',
                lat='lat'):
    '''
    功能：将表格中的经纬度生成delaunay三角形，每个三角形关联id编号
    df::DataFrame
    id_use::表中的id列名
    lon::经度列名
    lat::纬度列名
    return gdf 可以直接导出为图层
    '''
    df['lonlat'] = df[lon].map(str) + df[lat].map(str)
    points = MultiPoint([[lon,lat] for lon,lat in zip(df[lon],df[lat])])
    triangles = triangulate(points,tolerance=0.00001)
    gdf = gpd.GeoDataFrame(pd.DataFrame([[index,t] for index,t in enumerate(triangles)],columns=['id','geometry']),crs="epsg:4326",geometry='geometry')
    
    # Correctly extract coordinates from the triangle polygon
    gdf[['site1','site2','site3']] = gdf['geometry'].apply(
        lambda c: pd.Series([f"{xy[0]}{xy[1]}" for xy in c.exterior.coords[:3]])
    )

    for i in range(1,4):
        gdf = gdf.merge(df[[id_use,'lonlat']].rename(columns={id_use:f'{id_use}_{i}','lonlat':f'site{i}'}),how='left',on=f'site{i}')
    return gdf


def add_voronoi(data,lon='lon',lat='lat'):
    '''
    功能：将表格中的经纬度生成泰森多边形
    data::DataFrame
    lon::经度列名
    lat::纬度列名
    return gdf 可以直接导出为图层
    '''
    gdf = add_points(data,lon,lat)
    # 计算所有点的并集，作为泰森多边形的边界
    boundary = gdf.unary_union.convex_hull
    # 生成泰森多边形
    voronoi_polygons = voronoi_diagram(gdf.unary_union, envelope=boundary)
    
    # 创建一个GeoDataFrame来存储泰森多边形
    voronoi_gdf = gpd.GeoDataFrame(geometry=list(voronoi_polygons.geoms), crs="epsg:4326")
    
    # 将原始点与泰森多边形进行空间连接，以匹配属性
    # 注意：泰森多边形中的每个多边形都包含一个原始点
    joined_gdf = gpd.sjoin(voronoi_gdf, gdf, how="inner", op="contains")
    
    return joined_gdf

def distancea_str(lon1, lat1, lon2, lat2):
    """
    作用：计算两个经纬度点之间的距离
    lon1, lat1: float - 第一个点的经纬度
    lon2, lat2: float - 第二个点的经纬度
    return: float - 距离（米）
    """
    if any(v is None or np.isnan(v) for v in [lon1, lat1, lon2, lat2]):
        return None
    try:
        # 使用 WGS84 模型
        geod = Geodesic.WGS84
        result = geod.Inverse(lat1, lon1, lat2, lon2)
        return result['s12']
    except (ValueError, TypeError):
        return None

def distancea_df(data, lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2'):
    """
    作用：计算DataFrame中两对经纬度点之间的距离
    data: DataFrame - 包含经纬度列
    lon1, lat1: str - 第一对经纬度列名
    lon2, lat2: str - 第二对经纬度列名
    return: Series - 包含距离的Series
    """
    distances = data.apply(
        lambda row: distancea_str(row[lon1], row[lat1], row[lon2], row[lat2]),
        axis=1
    )
    return distances

def add_points(data,lon='lon',lat='lat'):
    '''
    作用：将一个带有经纬度的DataFrame转换成GeoDataFrame
    参数说明：
    data:DataFrame - 带有经纬度两列
    lon, lat: str - 经纬度字段名
    return GeoDataFrame
    '''
    data['geometry'] = [Point(xy) for xy in zip(data[lon], data[lat])]
    data_pot = gpd.GeoDataFrame(data, crs="epsg:4326", geometry='geometry')
    return data_pot

def gdf_to_kml(gdf, out_kml_path, name='name', description='description'):
    '''
    作用：将GeoDataFrame转换成kml文件
    参数说明：
    gdf: GeoDataFrame - 需要转换的GeoDataFrame
    out_kml_path: str - 输出的kml文件路径
    name: str - kml中每个要素的名称字段
    description: str - kml中每个要素的描述字段
    '''
    kml = simplekml.Kml()
    for index, row in gdf.iterrows():
        if isinstance(row.geometry, Point):
            pnt = kml.newpoint()
            pnt.name = str(row[name]) if name in row else ''
            pnt.description = str(row[description]) if description in row else ''
            pnt.coords = [(row.geometry.x, row.geometry.y)]
        elif isinstance(row.geometry, LineString):
            ls = kml.newlinestring()
            ls.name = str(row[name]) if name in row else ''
            ls.description = str(row[description]) if description in row else ''
            ls.coords = list(row.geometry.coords)
        elif isinstance(row.geometry, Polygon):
            pol = kml.newpolygon()
            pol.name = str(row[name]) if name in row else ''
            pol.description = str(row[description]) if description in row else ''
            pol.outerboundaryis = list(row.geometry.exterior.coords)
            if row.geometry.interiors:
                pol.innerboundaryis = [list(interior.coords) for interior in row.geometry.interiors]
    kml.save(out_kml_path)

def shp_to_kml(shp_path, out_kml_path, name='name', description='description'):
    '''
    作用：将shp文件转换成kml文件
    参数说明：
    shp_path: str - shp文件路径
    out_kml_path: str - 输出的kml文件路径
    name: str - kml中每个要素的名称字段
    description: str - kml中每个要素的描述字段
    '''
    gdf = gpd.read_file(shp_path, encoding='utf-8')
    gdf_to_kml(gdf, out_kml_path, name, description)

def kml_to_shp(kml_path, out_shp_path):
    '''
    作用：将kml文件转换成shp文件
    参数说明：
    kml_path: str - kml文件路径
    out_shp_path: str - 输出的shp文件路径
    '''
    # 创建一个临时目录来存放转换后的geojson
    temp_dir = "temp_kml_to_shp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        # kml2geojson 会在指定目录下生成 geojson 文件
        k2g.convert(kml_path, temp_dir)
        
        # 查找生成的geojson文件
        geojson_files = [f for f in os.listdir(temp_dir) if f.endswith('.geojson')]
        if not geojson_files:
            raise FileNotFoundError("kml to geojson conversion failed, no geojson file found.")
            
        # 读取第一个geojson文件
        gdf = gpd.read_file(os.path.join(temp_dir, geojson_files[0]))
        
        # 写入shp文件
        gdf.to_file(out_shp_path, encoding='utf-8')
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def wkt_to_shp(df, wkt_col, out_shp_path):
    '''
    作用：将含有wkt格式的DataFrame转换成shp文件
    参数说明：
    df: DataFrame - 含有wkt格式的DataFrame
    wkt_col: str - wkt所在的列名
    out_shp_path: str - 输出的shp文件路径
    '''
    df['geometry'] = df[wkt_col].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="epsg:4326")
    gdf.to_file(out_shp_path, encoding='utf-8')