"""
辅助函数用于地理空间数据处理

Author: Non-existent987
License: MIT
"""
import numpy as np
import pyproj
from typing import Tuple


def detect_crs(df, lon_col: str, lat_col: str) -> str:
    """
    检测DataFrame的坐标参考系统(CRS)
    
    通过坐标范围自动检测是否为 WGS84 (EPSG:4326) 坐标系
    
    Parameters
    ----------
    df : pd.DataFrame
        包含坐标数据的DataFrame
    lon_col : str
        经度列名
    lat_col : str
        纬度列名
    
    Returns
    -------
    str
        检测到的CRS，当前仅支持 'EPSG:4326'
    
    Raises
    ------
    ValueError
        如果坐标范围不符合WGS84标准
    """
    lons = df[lon_col].values
    lats = df[lat_col].values
    
    # 检查是否为WGS84范围
    lon_in_range = (-180 <= lons.min() <= 180) and (-180 <= lons.max() <= 180)
    lat_in_range = (-90 <= lats.min() <= 90) and (-90 <= lats.max() <= 90)
    
    if lon_in_range and lat_in_range:
        return 'EPSG:4326'
    else:
        raise ValueError(
            f"坐标范围不符合WGS84 (EPSG:4326) 标准。\n"
            f"经度范围: [{lons.min():.4f}, {lons.max():.4f}] (应在 [-180, 180])\n"
            f"纬度范围: [{lats.min():.4f}, {lats.max():.4f}] (应在 [-90, 90])\n"
            f"请检查您的坐标系统或坐标列是否正确，支持经纬度数据。"
        )


def create_projected_kdtree(df, lon_col: str = 'lon', lat_col: str = 'lat') -> Tuple[np.ndarray, str]:
    """
    将WGS84经纬度坐标转换为UTM投影坐标
    
    根据数据中心点自动选择合适的UTM投影带，将地理坐标转换为平面坐标（米）
    
    Parameters
    ----------
    df : pd.DataFrame
        包含WGS84坐标的DataFrame
    lon_col : str, default='lon'
        经度列名
    lat_col : str, default='lat'
        纬度列名
    
    Returns
    -------
    points : np.ndarray
        转换后的UTM坐标数组，形状为 (n, 2)，单位为米
    epsg_code : str
        使用的UTM投影EPSG代码，格式如 'EPSG:32650'
    
    Notes
    -----
    - UTM投影会根据数据中心点自动选择投影带
    - 北半球使用 EPSG:326xx，南半球使用 EPSG:327xx
    - 投影后的坐标单位为米，适合进行距离计算
    """
    lons = df[lon_col].values
    lats = df[lat_col].values
    
    # 确定中心点（用于选择UTM区域）
    center_lon, center_lat = np.mean(lons), np.mean(lats)
    utm_zone = int((center_lon + 180) / 6) + 1
    hemisphere = 'north' if center_lat >= 0 else 'south'
    
    # EPSG code for WGS 84 / UTM zone
    epsg_code = 32600 + utm_zone if hemisphere == 'north' else 32700 + utm_zone
    
    # 创建转换器（从WGS84到UTM）
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", 
        f"EPSG:{epsg_code}", 
        always_xy=True
    )
    
    # 转换为UTM坐标
    x, y = transformer.transform(lons, lats)
    points = np.column_stack((x, y))
    
    return points, f"EPSG:{epsg_code}"