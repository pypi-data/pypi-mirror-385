import tablegis as tg
import pytest
import pandas as pd
import numpy as np
from tablegis.utils import to_lonlat, wgs84_to_gcj02, gcj02_to_wgs84, wgs84_to_bd09, bd09_to_wgs84, transform

def test_min_distance_onetable():
    """测试 min_distance_onetable 函数"""
    
    # 测试用例1: 基本功能测试 - 查找最近1个点
    df = pd.DataFrame({
        'id': ['p1', 'p2', 'p3'],
        'lon': [114.01, 114.05, 114.12],
        'lat': [30.01, 30.05, 30.12]
    })
    
    result = tg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=1)
    
    # 验证返回的DataFrame包含正确的列
    assert 'nearest1_id' in result.columns
    assert 'nearest1_lon' in result.columns
    assert 'nearest1_lat' in result.columns
    assert 'nearest1_distance' in result.columns
    
    # 验证p1的最近点是p2
    assert result.loc[0, 'nearest1_id'] == 'p2'
    # 验证距离是正数
    assert result.loc[0, 'nearest1_distance'] > 0
    
    # 测试用例2: 查找最近2个点
    result2 = tg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=2)
    
    # 验证包含mean_distance列
    assert 'mean_distance' in result2.columns
    assert 'nearest2_id' in result2.columns
    
    # 验证平均距离计算正确
    assert not pd.isna(result2.loc[0, 'mean_distance'])
    
    # 测试用例3: 包含自身点
    result3 = tg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=1, include_self=True)
    
    # 验证每个点的最近点是自己
    for i in range(len(df)):
        assert result3.loc[i, 'nearest1_id'] == df.loc[i, 'id']
        assert result3.loc[i, 'nearest1_distance'] == 0.0
    
    # 测试用例4: 自定义列名
    df_custom = pd.DataFrame({
        'point_id': ['A', 'B', 'C'],
        'longitude': [116.403, 116.407, 116.404],
        'latitude': [39.914, 39.918, 39.916]
    })
    
    result4 = tg.min_distance_onetable(df_custom, lon='longitude', lat='latitude', idname='point_id', n=1)
    assert 'nearest1_point_id' in result4.columns
    
    # 测试用例5: 边界情况 - 空DataFrame
    df_empty = pd.DataFrame({'id': [], 'lon': [], 'lat': []})
    result5 = tg.min_distance_onetable(df_empty, lon='lon', lat='lat', idname='id', n=1)
    assert len(result5) == 0
    
    # 测试用例6: 边界情况 - 单个点
    df_single = pd.DataFrame({
        'id': ['p1'],
        'lon': [114.01],
        'lat': [30.01]
    })
    result6 = tg.min_distance_onetable(df_single, lon='lon', lat='lat', idname='id', n=1)
    assert pd.isna(result6.loc[0, 'nearest1_id'])
    
    # 测试用例7: 异常处理 - n < 1
    with pytest.raises(ValueError, match="n must be > 0"):
        tg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=0)
    
    # 测试用例8: 异常处理 - 列名不存在
    with pytest.raises(ValueError, match="Longitude or latitude column not found"):
        tg.min_distance_onetable(df, lon='wrong_lon', lat='lat', idname='id', n=1)
    
    with pytest.raises(ValueError, match="ID column not found"):
        tg.min_distance_onetable(df, lon='lon', lat='lat', idname='wrong_id', n=1)
    
    print("✓ test_min_distance_onetable 所有测试通过!")


def test_min_distance_twotable():
    """测试 min_distance_twotable 函数"""
    
    # 测试用例1: 基本功能测试
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

    result = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                    lon2='lon2', lat2='lat2', df2_id='id', n=1)
    
    # 验证返回的DataFrame包含正确的列
    assert 'nearest1_id' in result.columns
    assert 'nearest1_lon2' in result.columns
    assert 'nearest1_lat2' in result.columns
    assert 'nearest1_distance' in result.columns
    
    # 验证原始df1的列都保留
    assert 'lon1' in result.columns
    assert 'lat1' in result.columns
    
    # 验证距离都是正数
    assert all(result['nearest1_distance'] >= 0)
    
    # 测试用例2: 查找最近2个点
    result2 = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=2)
    
    # 验证包含mean_distance列
    assert 'mean_distance' in result2.columns
    assert 'nearest2_id' in result2.columns
    
    # 验证平均距离不为空
    assert not pd.isna(result2.loc[0, 'mean_distance'])
    
    # 测试用例3: n大于df2的点数
    result3 = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=5)
    
    # 验证超出的列被填充为NaN
    assert pd.isna(result3.loc[0, 'nearest4_id'])
    assert pd.isna(result3.loc[0, 'nearest5_distance'])
    
    # 测试用例4: 边界情况 - 空DataFrame
    df_empty = pd.DataFrame({'id': [], 'lon2': [], 'lat2': []})
    result4 = tg.min_distance_twotable(df1, df_empty, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=1)
    assert pd.isna(result4.loc[0, 'nearest1_id'])
    
    # 测试用例5: 异常处理 - n < 1
    with pytest.raises(ValueError, match="参数 n 必须大于等于 1"):
        tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                             lon2='lon2', lat2='lat2', df2_id='id', n=0)
    
    # 测试用例6: 指定CRS参数
    result6 = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=1,
                                     crs1='EPSG:4326', crs2='EPSG:4326')
    assert 'nearest1_distance' in result6.columns
    
    # 测试用例7: 自定义df2_id列名
    df2_custom = df2.copy()
    df2_custom = df2_custom.rename(columns={'id': 'point_name'})
    result7 = tg.min_distance_twotable(df1, df2_custom, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='point_name', n=1)
    assert 'nearest1_point_name' in result7.columns
    
    print("✓ test_min_distance_twotable 所有测试通过!")



def test_wgs84_to_gcj02_and_nan():
    df = pd.DataFrame({
        "lon": [116.397487, np.nan],
        "lat": [39.908722, np.nan],
    })
    out = tg.to_lonlat(df, "lon", "lat", from_crs="wgs84", to_crs="gcj02")
    # 第一个点与标量函数结果接近
    exp_lon, exp_lat = wgs84_to_gcj02(116.397487, 39.908722)
    assert np.isclose(out.loc[0, "gcj02_lon"], exp_lon, atol=1e-6)
    assert np.isclose(out.loc[0, "gcj02_lat"], exp_lat, atol=1e-6)
    # 第二行原本是 nan，目标列也是 nan
    assert np.isnan(out.loc[1, "gcj02_lon"])
    assert np.isnan(out.loc[1, "gcj02_lat"])
    print("✓ test_wgs84_to_gcj02_and_nan 所有测试通过!")

def test_bd09_to_wgs84_roundtrip():
    # 先由 WGS84 生成 BD09，再从 BD09 转回 WGS84
    lon, lat = 116.397487, 39.908722
    bd_lon, bd_lat = wgs84_to_bd09(lon, lat)
    df = pd.DataFrame({"lon": [bd_lon], "lat": [bd_lat]})
    out = tg.to_lonlat(df, "lon", "lat", from_crs="bd09", to_crs="wgs84")
    # 反算应接近原始 WGS84（允许少量偏差）
    assert np.isclose(out.loc[0, "wgs84_lon"], lon, atol=1e-6)
    assert np.isclose(out.loc[0, "wgs84_lat"], lat, atol=1e-6)
    print("✓ test_bd09_to_wgs84_roundtrip 所有测试通过!")

def test_webmercator_and_back():
    # WGS84 -> WebMercator -> WGS84
    lon, lat = 116.397487, 39.908722
    # 先生成 web mercator
    mx, my = transform(lon, lat, "wgs84", "web_mercator")
    df = pd.DataFrame({"lon": [mx], "lat": [my]})
    out = tg.to_lonlat(df, "lon", "lat", from_crs="web_mercator", to_crs="wgs84")
    assert np.isclose(out.loc[0, "wgs84_lon"], lon, atol=1e-6)
    assert np.isclose(out.loc[0, "wgs84_lat"], lat, atol=1e-6)
    print("✓ test_webmercator_and_back 所有测试通过!")

def test_unknown_crs_raises():
    df = pd.DataFrame({"lon": [116.4], "lat": [39.9]})
    with pytest.raises(ValueError):
        tg.to_lonlat(df, "lon", "lat", from_crs="unknown", to_crs="wgs84")
    with pytest.raises(ValueError):
        tg.to_lonlat(df, "lon", "lat", from_crs="wgs84", to_crs="unknown")
    print("✓ test_unknown_crs_raises 所有测试通过!")


if __name__ == "__main__":
    test_min_distance_onetable()
    test_min_distance_twotable()
    test_wgs84_to_gcj02_and_nan()
    test_bd09_to_wgs84_roundtrip()
    test_webmercator_and_back()
    test_unknown_crs_raises()