"""
Python tests for geographic_midpoint.py.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""
from sidpy.geographic_midpoint.geographic_midpoint import Geographic_Midpoint
from datetime import datetime


def test_to_cart():
    geo = Geographic_Midpoint()
    assert geo.to_cart(lat=0, lon=0) == [1.0, 0.0, 0.0]


def test_weighted_avg_coord():
    geo = Geographic_Midpoint()
    point_1, point_2 = [10, 10, 10], [0, 0, 0]
    assert geo.weighted_avg_coord(point_1, point_2) == (5.0, 5.0, 5.0)
    weight_1, weight_2 = 4.0, 1.0
    assert geo.weighted_avg_coord(point_1, point_2, weight_1, weight_2) == (8.0, 8.0, 8.0)


def test_to_latlon():
    geo = Geographic_Midpoint()
    assert geo.to_latlon(1.0, 0.0, 0.0) == (0.0, 0.0)


def test_calc_midpoint():
    geo = Geographic_Midpoint()
    point_1, point_2 = [10, 10], [0, 0]
    mid = geo.calc_midpoint(point_1, point_2)
    assert (round(mid[0]), round(mid[1])) == (5, 5)


def test_sunrise_sunset():
    geo = Geographic_Midpoint()
    sunrise, sunset = geo.sunrise_sunset(datetime(year=2020, month=1, day=1), 0, 0)
    assert sunrise.strftime("%Y/%m/%d %H:%M:%S:%f") == '2020/01/01 05:59:46:642588'
    assert sunset.strftime("%Y/%m/%d %H:%M:%S:%f") == '2020/01/01 18:06:52:306438'
