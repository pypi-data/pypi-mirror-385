import pandasgeo as pdg
import pytest
import pandas as pd


def test_min_distance_onetable():
    """测试 min_distance_onetable 函数"""
    
    # 测试用例1: 基本功能测试 - 查找最近1个点
    df = pd.DataFrame({
        'id': ['p1', 'p2', 'p3'],
        'lon': [114.01, 114.05, 114.12],
        'lat': [30.01, 30.05, 30.12]
    })
    
    result = pdg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=1)
    
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
    result2 = pdg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=2)
    
    # 验证包含mean_distance列
    assert 'mean_distance' in result2.columns
    assert 'nearest2_id' in result2.columns
    
    # 验证平均距离计算正确
    assert not pd.isna(result2.loc[0, 'mean_distance'])
    
    # 测试用例3: 包含自身点
    result3 = pdg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=1, include_self=True)
    
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
    
    result4 = pdg.min_distance_onetable(df_custom, lon='longitude', lat='latitude', idname='point_id', n=1)
    assert 'nearest1_point_id' in result4.columns
    
    # 测试用例5: 边界情况 - 空DataFrame
    df_empty = pd.DataFrame({'id': [], 'lon': [], 'lat': []})
    result5 = pdg.min_distance_onetable(df_empty, lon='lon', lat='lat', idname='id', n=1)
    assert len(result5) == 0
    
    # 测试用例6: 边界情况 - 单个点
    df_single = pd.DataFrame({
        'id': ['p1'],
        'lon': [114.01],
        'lat': [30.01]
    })
    result6 = pdg.min_distance_onetable(df_single, lon='lon', lat='lat', idname='id', n=1)
    assert pd.isna(result6.loc[0, 'nearest1_id'])
    
    # 测试用例7: 异常处理 - n < 1
    with pytest.raises(ValueError, match="n must be > 0"):
        pdg.min_distance_onetable(df, lon='lon', lat='lat', idname='id', n=0)
    
    # 测试用例8: 异常处理 - 列名不存在
    with pytest.raises(ValueError, match="Longitude or latitude column not found"):
        pdg.min_distance_onetable(df, lon='wrong_lon', lat='lat', idname='id', n=1)
    
    with pytest.raises(ValueError, match="ID column not found"):
        pdg.min_distance_onetable(df, lon='lon', lat='lat', idname='wrong_id', n=1)
    
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

    result = pdg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
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
    result2 = pdg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=2)
    
    # 验证包含mean_distance列
    assert 'mean_distance' in result2.columns
    assert 'nearest2_id' in result2.columns
    
    # 验证平均距离不为空
    assert not pd.isna(result2.loc[0, 'mean_distance'])
    
    # 测试用例3: n大于df2的点数
    result3 = pdg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=5)
    
    # 验证超出的列被填充为NaN
    assert pd.isna(result3.loc[0, 'nearest4_id'])
    assert pd.isna(result3.loc[0, 'nearest5_distance'])
    
    # 测试用例4: 边界情况 - 空DataFrame
    df_empty = pd.DataFrame({'id': [], 'lon2': [], 'lat2': []})
    result4 = pdg.min_distance_twotable(df1, df_empty, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=1)
    assert pd.isna(result4.loc[0, 'nearest1_id'])
    
    # 测试用例5: 异常处理 - n < 1
    with pytest.raises(ValueError, match="参数 n 必须大于等于 1"):
        pdg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                             lon2='lon2', lat2='lat2', df2_id='id', n=0)
    
    # 测试用例6: 指定CRS参数
    result6 = pdg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='id', n=1,
                                     crs1='EPSG:4326', crs2='EPSG:4326')
    assert 'nearest1_distance' in result6.columns
    
    # 测试用例7: 自定义df2_id列名
    df2_custom = df2.copy()
    df2_custom.rename(columns={'id': 'point_name'}, inplace=True)
    
    result7 = pdg.min_distance_twotable(df1, df2_custom, lon1='lon1', lat1='lat1', 
                                     lon2='lon2', lat2='lat2', df2_id='point_name', n=1)
    assert 'nearest1_point_name' in result7.columns
    
    print("✓ test_min_distance_twotable 所有测试通过!")

def test_distancea_str():
    """
    测试 distancea_str 函数计算两个点之间的距离。
    """
    # 定义两个点，位于赤道上，经度相差1度
    lon1, lat1 = 0, 0
    lon2, lat2 = 1, 0

    # 在赤道上，1度的经度差大约是 111.32 公里
    expected_distance_meters = 111319.49

    # 调用函数计算距离
    calculated_distance = pdg.distancea_str(lon1, lat1, lon2, lat2)

    # 使用 pytest.approx 来比较浮点数，允许有一定的误差
    assert calculated_distance == pytest.approx(expected_distance_meters, rel=1e-4)
    print("✓ test_distancea_str 所有测试通过!")

def test_add_points():
    """
    测试 add_points 函数是否能正确将DataFrame转换为GeoDataFrame。
    """
    import pandas as pd
    from shapely.geometry import Point

    # 创建一个简单的DataFrame
    data = {'id': ['A', 'B'], 'lon': [10, 20], 'lat': [30, 40]}
    df = pd.DataFrame(data)

    # 调用函数
    gdf = pdg.add_points(df, lon='lon', lat='lat')

    # 验证返回的是否是GeoDataFrame
    assert 'geometry' in gdf.columns
    # 验证第一个点的坐标是否正确
    assert gdf.geometry.iloc[0] == Point(10, 30)
    # 验证行数是否保持不变
    assert len(gdf) == len(df)
    print("✓ test_add_points 所有测试通过!")
if __name__ == "__main__":
    test_min_distance_onetable()
    test_min_distance_twotable()
    test_distancea_str()
    test_add_points()