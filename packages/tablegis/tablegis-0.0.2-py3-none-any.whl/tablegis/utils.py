"""
辅助函数用于地理空间数据处理

Author: Non-existent987
License: MIT
"""
import numpy as np
import pyproj
from typing import Tuple
from math import sin, cos, sqrt, atan2, pi
from pyproj import Transformer, CRS
# import pandas as pd
import numpy as np


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



# ----------------------------
# 内部：GCJ02 / BD09 算法（点级）
# ----------------------------
PI = pi
A = 6378245.0  # a, 长半轴
EE = 0.00669342162296594323  # 偏心率平方

def _out_of_china(lon, lat):
    return not (73.66 <= lon <= 135.05 and 3.86 <= lat <= 53.55)

def _transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * (sqrt(abs(x)))
    ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * sin(y / 12.0 * PI) + 320 * sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret

def _transform_lon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x))
    ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret

def wgs84_to_gcj02(lon, lat):
    if _out_of_china(lon, lat):
        return lon, lat
    dLat = _transform_lat(lon - 105.0, lat - 35.0)
    dLon = _transform_lon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * PI
    magic = sin(radLat)
    magic = 1 - EE * magic * magic
    sqrtMagic = sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (A / sqrtMagic * cos(radLat) * PI)
    mgLat = lat + dLat
    mgLon = lon + dLon
    return mgLon, mgLat

def _delta(lon, lat):
    dLat = _transform_lat(lon - 105.0, lat - 35.0)
    dLon = _transform_lon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * PI
    magic = sin(radLat)
    magic = 1 - EE * magic * magic
    sqrtMagic = sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (A / sqrtMagic * cos(radLat) * PI)
    return dLon, dLat

def gcj02_to_wgs84(lon, lat):
    if _out_of_china(lon, lat):
        return lon, lat
    # 迭代法反算
    lon0 = lon
    lat0 = lat
    for i in range(10):
        dlon, dlat = _delta(lon0, lat0)
        lon1 = lon - dlon
        lat1 = lat - dlat
        if abs(lon1 - lon0) < 1e-9 and abs(lat1 - lat0) < 1e-9:
            lon0, lat0 = lon1, lat1
            break
        lon0, lat0 = lon1, lat1
    return lon0, lat0

def gcj02_to_bd09(lon, lat):
    x = lon
    y = lat
    z = sqrt(x * x + y * y) + 0.00002 * sin(y * PI * 3000.0 / 180.0)
    theta = atan2(y, x) + 0.000003 * cos(x * PI * 3000.0 / 180.0)
    bd_lon = z * cos(theta) + 0.0065
    bd_lat = z * sin(theta) + 0.006
    return bd_lon, bd_lat

def bd09_to_gcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * PI * 3000.0 / 180.0)
    theta = atan2(y, x) - 0.000003 * cos(x * PI * 3000.0 / 180.0)
    gg_lon = z * cos(theta)
    gg_lat = z * sin(theta)
    return gg_lon, gg_lat

def wgs84_to_bd09(lon, lat):
    lon2, lat2 = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon2, lat2)

def bd09_to_wgs84(lon, lat):
    lon2, lat2 = bd09_to_gcj02(lon, lat)
    return gcj02_to_wgs84(lon2, lat2)

# ----------------------------
# pyproj Transformer 缓存与封装（WGS84/3857/CGCS2000）
# ----------------------------
_transformers_cache = {}

def _get_transformer(from_epsg_or_crs, to_epsg_or_crs):
    key = (str(from_epsg_or_crs), str(to_epsg_or_crs))
    if key in _transformers_cache:
        return _transformers_cache[key]
    t = Transformer.from_crs(CRS.from_user_input(from_epsg_or_crs),
                             CRS.from_user_input(to_epsg_or_crs),
                             always_xy=True)
    _transformers_cache[key] = t
    return t

_CRS_MAP = {
    "wgs84": "EPSG:4326",
    "web_mercator": "EPSG:3857",
    "cgcs2000": "EPSG:4490",
}

# 统一 transform（保留原有）
def transform(lon, lat, from_crs, to_crs):
    from_crs = from_crs.lower()
    to_crs = to_crs.lower()
    if from_crs == to_crs:
        return lon, lat

    standard = ("wgs84", "web_mercator", "cgcs2000")
    if from_crs in standard and to_crs in standard:
        t = _get_transformer(_CRS_MAP[from_crs], _CRS_MAP[to_crs])
        x, y = t.transform(lon, lat)
        return x, y

    def to_wgs84_if_needed(lon_, lat_, crs_):
        if crs_ == "wgs84":
            return lon_, lat_
        if crs_ == "gcj02":
            return gcj02_to_wgs84(lon_, lat_)
        if crs_ == "bd09":
            return bd09_to_wgs84(lon_, lat_)
        if crs_ == "web_mercator":
            t = _get_transformer(_CRS_MAP["web_mercator"], _CRS_MAP["wgs84"])
            return t.transform(lon_, lat_)
        if crs_ == "cgcs2000":
            t = _get_transformer(_CRS_MAP["cgcs2000"], _CRS_MAP["wgs84"])
            return t.transform(lon_, lat_)
        raise ValueError("未知的输入 CRS: " + crs_)

    def from_wgs84_if_needed(lon_, lat_, crs_):
        if crs_ == "wgs84":
            return lon_, lat_
        if crs_ == "gcj02":
            return wgs84_to_gcj02(lon_, lat_)
        if crs_ == "bd09":
            return wgs84_to_bd09(lon_, lat_)
        if crs_ == "web_mercator":
            t = _get_transformer(_CRS_MAP["wgs84"], _CRS_MAP["web_mercator"])
            return t.transform(lon_, lat_)
        if crs_ == "cgcs2000":
            t = _get_transformer(_CRS_MAP["wgs84"], _CRS_MAP["cgcs2000"])
            return t.transform(lon_, lat_)
        raise ValueError("未知的目标 CRS: " + crs_)

    lon_w, lat_w = to_wgs84_if_needed(lon, lat, from_crs)
    lon_out, lat_out = from_wgs84_if_needed(lon_w, lat_w, to_crs)
    return lon_out, lat_out

# ----------------------------
# 批量/表格转换 to_lonlat
# ----------------------------
_SUPPORTED_CRS = {"wgs84", "web_mercator", "cgcs2000", "gcj02", "bd09"}

def _apply_pointwise(fn, xs, ys):
    # fn: (lon, lat) -> (lon2, lat2)
    out_lon = []
    out_lat = []
    for x, y in zip(xs, ys):
        if x is None or y is None or (isinstance(x, float) and np.isnan(x)) or (isinstance(y, float) and np.isnan(y)):
            out_lon.append(np.nan)
            out_lat.append(np.nan)
        else:
            lon2, lat2 = fn(float(x), float(y))
            out_lon.append(lon2)
            out_lat.append(lat2)
    return np.array(out_lon, dtype=float), np.array(out_lat, dtype=float)
def to_lonlat_utils(df, lon, lat, from_crs, to_crs):
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
    from_crs = from_crs.lower()
    to_crs = to_crs.lower()
    if from_crs not in _SUPPORTED_CRS:
        raise ValueError(f"未知的 from_crs: {from_crs}")
    if to_crs not in _SUPPORTED_CRS:
        raise ValueError(f"未知的 to_crs: {to_crs}")
    df = df.copy()

    if lon not in df.columns or lat not in df.columns:
        raise KeyError(f"DataFrame 中缺少列: {lon} 或 {lat}")

    xs = df[lon].to_numpy()
    ys = df[lat].to_numpy()

    # 1) 若 from_crs 和 to_crs 都是标准 CRS -> 用 pyproj 批量转换
    standard = ("wgs84", "web_mercator", "cgcs2000")
    target_lon_col = f"{to_crs}_lon"
    target_lat_col = f"{to_crs}_lat"

    if from_crs in standard and to_crs in standard:
        t = _get_transformer(_CRS_MAP[from_crs], _CRS_MAP[to_crs])
        # Transformer.transform 可以接受 ndarray
        xs_f = xs.astype(float)
        ys_f = ys.astype(float)
        # 保持对 NaN 的支持: pyproj 对 NaN 通常会返回 nan
        out_x, out_y = t.transform(xs_f, ys_f)
        df[target_lon_col] = out_x
        df[target_lat_col] = out_y
        return df

    # 2) 先把输入转换到 WGS84（批量或点级）
    if from_crs == "wgs84":
        wgs_x = xs.astype(float)
        wgs_y = ys.astype(float)
    elif from_crs in ("web_mercator", "cgcs2000"):
        t = _get_transformer(_CRS_MAP[from_crs], _CRS_MAP["wgs84"])
        wgs_x, wgs_y = t.transform(xs.astype(float), ys.astype(float))
    elif from_crs == "gcj02":
        wgs_x, wgs_y = _apply_pointwise(gcj02_to_wgs84, xs, ys)
    elif from_crs == "bd09":
        wgs_x, wgs_y = _apply_pointwise(bd09_to_wgs84, xs, ys)
    else:
        # 不会到这儿，因为前面已校验
        raise ValueError("不支持的 from_crs")

    # 3) 从 WGS84 转到目标 CRS（批量或点级）
    if to_crs == "wgs84":
        df[target_lon_col] = wgs_x
        df[target_lat_col] = wgs_y
        return df
    elif to_crs in ("web_mercator", "cgcs2000"):
        t2 = _get_transformer(_CRS_MAP["wgs84"], _CRS_MAP[to_crs])
        out_x, out_y = t2.transform(wgs_x, wgs_y)
        df[target_lon_col] = out_x
        df[target_lat_col] = out_y
        return df
    elif to_crs == "gcj02":
        out_x, out_y = _apply_pointwise(wgs84_to_gcj02, wgs_x, wgs_y)
        df[target_lon_col] = out_x
        df[target_lat_col] = out_y
        return df
    elif to_crs == "bd09":
        out_x, out_y = _apply_pointwise(wgs84_to_bd09, wgs_x, wgs_y)
        df[target_lon_col] = out_x
        df[target_lat_col] = out_y
        return df

    # 防护（不应到达）
    raise RuntimeError("Unhandled CRS conversion path")