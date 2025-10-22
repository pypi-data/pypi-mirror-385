#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
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
    import tablegis as tg

    # 创建两个示例DataFrame
    df2 = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'lon2': [116.403, 116.407, 116.404, 116.408],
        'lat2': [39.914, 39.918, 39.916, 39.919]
    })

    # 计算最近的1个点
    result = tg.min_distance_onetable(df2,'lon2','lat2',idname='id',n=1)
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
    result = tg.min_distance_twotable(df1, df2,lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2', df2_id='id', n=1)
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

def to_lonlat(df, lon, lat, from_crs, to_crs):
    """
    作用：在df上添加转换后的经纬度'。
    - df:DataFrame
    - lon, lat: 列名（字符串）
    - from_crs, to_crs: 支持的坐标系标识{"wgs84", "web_mercator", "cgcs2000", "gcj02", "bd09"}
        - "wgs84"       : EPSG:4326 (经纬度，WGS84，GPS 设备、北斗原始数据，通俗意义上的经纬度)
        - "web_mercator": EPSG:3857 (Web Mercator，Web地图采用，单位：米)
        - "cgcs2000"    : EPSG:4490 (中国国家大地坐标系，用于官方测绘、国土等领域)
        - "gcj02"       : 中国火星坐标系（加密偏移，高德、腾讯、谷歌中国地图等采用）
        - "bd09"        : 百度坐标系（在 GCJ02 基础上再加密，百度地图专用）
    返回：带新增列的 DataFrame
    抛错：当 from_crs 或 to_crs 非支持集合时抛 ValueError
    """
    return to_lonlat_utils(df, lon, lat, from_crs, to_crs)