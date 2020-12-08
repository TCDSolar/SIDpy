"""
Calculate the weighted geographic midpoint between a set of given lat and lon
values. The sunrise and sunset times are then calculated at the geographic
midpoint.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import math

from astral import Observer, sun


class Geographic_Midpoint:
    """ Calculate the weighted geographic midpoint and sunrise/sunset times
    between a set of given lat and lon values.
    """

    def calc_midpoint(self, point1, point2):
        """
        Calculate the geographic midpoint for two points
        given their lat and lon.

        Parameters
        ----------
        point1 : list
            lat & lon respectively for point1.
        point2 : list
            lat & lon respectively for point2.

        Returns
        -------
        midpoint : list
            midpoint lat & lon respectively.
        """
        point1 = self.to_cart(point1[0], point1[1])
        point2 = self.to_cart(point2[0], point2[1])
        x, y, z = self.weighted_avg_coord(point1, point2)
        midpoint = self.to_latlon(x, y, z)
        return midpoint

    def to_cart(self, lat, lon):
        """
        Convert lat and lon to 3D cartesian coords.

        Parameters
        ----------
        lat : int
            Point latitude.
        lon : int
            Point longitude.

        Returns
        -------
        cart : list
            Cartessian coords; x, y, z.

        """
        lat = lat * math.pi / 180.0
        lon = lon * math.pi / 180.0
        x = math.cos(lat) * math.cos(lon)
        y = math.cos(lat) * math.sin(lon)
        z = math.sin(lat)
        cart = [x, y, z]
        return cart

    def weighted_avg_coord(self, point1, point2, w1=1, w2=1):
        """
        Find mean of two 3D cartessian points,
        this may be weighted using w1 & w2.

        Parameters
        ----------
        point1 : list
            3D cartessian coord.
        point2 : list
            3D cartessian coord.
        w1 : int
            Point1 weighting, default 1.
        w2 : int
            Point1 weighting, default 2.

        Returns
        -------
        x : int
            X position.
        y : int
            Y position.
        z : int
            Z position.

        """
        x = (point1[0] * w1 + point2[0] * w2) / (w1 + w2)
        y = (point1[1] * w1 + point2[1] * w2) / (w1 + w2)
        z = (point1[2] * w1 + point2[2] * w2) / (w1 + w2)
        return x, y, z

    def to_latlon(self, x, y, z):
        """
        Convert cartessian 3D point into lat and lon.

        Parameters
        ----------
        x : int
            X position.
        y : int
            Y position.
        z : int
            Z position.

        Returns
        -------
        lat : int
            Point latitude.
        lon : int
            Point longitude.

        """
        lon = math.atan2(y, x)
        hyp = math.sqrt(x * x + y * y)
        lat = math.atan2(z, hyp)
        lat = lat * 180.0 / math.pi
        lon = lon * 180.0 / math.pi
        return lat, lon

    def sunrise_sunset(self, date, lat, lon):
        """
        Calculate sunrise and sunset times in utc for given date,
        lat and lon.
        Parameters
        ----------
        date : datetime.date
            Date in yyyy-mm-dd.
        lat : int
            Latitude.
        lon : int
            Longitude.
        Returns
        -------
        sunrise : datetime
            Sunrise time.
        sunset : datetime
            Sunset time.
        """
        obs = Observer(latitude=lat, longitude=lon, elevation=0.0)
        sunrise = sun.sunrise(observer=obs, date=date)
        sunset = sun.sunset(observer=obs, date=date)
        return sunrise, sunset
