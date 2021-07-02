"""
Client containing functions specific to the processing of SuperSID VLF data;
reading csv files, get data from csv, get header information from csv,
normalize data, convert data to pandas DataFrame, plot data and create summary
plot.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import dates
from sunpy.time import parse_time

from supersid.config.config import archive_path as config_archive, transmitters
from supersid.geographic_midpoint.geographic_midpoint import Geographic_Midpoint

np.seterr(divide='ignore')
pd.options.mode.chained_assignment = None


class VLFClient:
    """
    """

    @staticmethod
    def read_csv(filename):
        """
        Read .csv files containing signal strength and time.

        Parameters
        ----------
        filename : str
            Path to csv file.

        Returns
        -------
        df : object
            Pandas dataframe containing csv data.
        """
        df = pd.read_csv(filename,
                         skipinitialspace=True,
                         delimiter=',',
                         names=['datetime', 'signal_strength'])
        return df

    def get_data(self, df):
        """
        Generate new dataframe containing only datetime and signal
        intensity with comments removed.

        Parameters
        ----------
        df : object
            Pandas dataframe containing csv data.

        Returns
        -------
        df : object
            Pandas dataframe containing normalized csv data without comments.
        """
        df = df[~df['datetime'].astype(str).str.startswith('#')]
        df['datetime'] = pd.to_datetime(df['datetime'],
                                        format='%Y-%m-%d %H:%M:%S')
        df = self.db_data(df)
        return df

    @staticmethod
    def get_header(df):
        """
        Process csv comments into file parameters.

        Parameters
        ----------
        df : object
            Pandas dataframe containing csv data.

        Returns
        -------
        parameters : dict
            Dictionary containing observation parameters, eg. transmitter freq.
        """
        parameters_dict = {}
        for index, row in df.iterrows():
            if (row[0])[0] == '#':
                row = row['datetime'][1:].replace(" ", "").rstrip('\n')
                para = row.split('=')
                if len(para) == 2:
                    parameters_dict[para[0]] = para[1]
        return parameters_dict

    @staticmethod
    def db_data(df):
        """
        Takes pandas dataframe and converts signal strength intensity to db.

        Parameters
        ----------
        df : object
            Pandas dataframe containing csv data.

        Returns
        -------
        df : object
            Pandas dataframe containing csv data in db.
        """
        df['signal_strength'] = 20 * np.log10(df['signal_strength'])
        return df

    @staticmethod
    def get_recent_goes():
        """
        Pull the most recent GOES X-ray data from the NOAA page

        Returns
        -------
        gl : pd.DataFrame object
                The GOES long channels as pandas series
        gs : pd.DataFrame object
                The GOES short channels as pandas series
        """
        data = pd.read_json("https://services.swpc.noaa.gov/json" +
                            "/goes/primary/xrays-7-day.json")
        data_short = data[data["energy"] == "0.05-0.4nm"]
        data_long = data[data["energy"] == "0.1-0.8nm"]
        time_array = [parse_time(x).datetime for x in
                      data_short['time_tag'].values]

        gl = pd.Series(data_long["flux"].values, index=time_array)
        gs = pd.Series(data_short["flux"].values, index=time_array)
        return gl, gs

    def create_plot_xrs(self, header, data, file_path, gl, gs):
        """
        Generate plot for given parameters and data.

        Parameters
        ----------
        header : dict
            Dictionary containing observation parameters, eg. transmitter freq.
        data : object
            Pandas dataframe containing csv data.
        file_path : str
            Path to csv file.
        gl : pandas.timeseries
            GOES XRS Long data.
        gs : pandas.timeseries
            GOES XRS Short data.

        Returns
        -------
        image_path : str
            Path to image location.
        """
        fig, ax = plt.subplots(2, sharex=True, figsize=(9, 6))
        # Get local sunrise and sunset markers.
        geo = Geographic_Midpoint()
        date_time_obj = datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S')
        try:
            sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), 53.33, 6.25)
            ax[0].axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Local Sunrise')
            ax[0].axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Local Sunset')
        except ValueError:
            print("Sun is always above the horizon on this day, at this location.")
        # Plot VLF data.

        sid = pd.Series(data['signal_strength'].values, index=pd.to_datetime(data['datetime']))
        if date_time_obj.date() == datetime.utcnow().date():
            sid = sid.truncate(after=datetime.utcnow().replace(minute=0, second=0)
                                     - timedelta(seconds=20))
        ax[0].plot(sid, color='k')
        ax[0].xaxis.set_major_locator(dates.HourLocator(interval=2))
        ax[0].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
        # Display time generated.
        ax[1].text(0.875, 0.03, 'Generated : ' + datetime.utcnow().strftime('%d-%b-%y %H:%M') + ' UTC',
                   horizontalalignment='center', verticalalignment='center', transform=ax[1].transAxes,
                   fontsize=8)
        # Plot GOES Long and Short XRS.
        ax[1].plot(gl, color='r', label=r'GOES 1.0-8.0 $\AA$')
        ax[1].plot(gs, color='b', label=r'GOES 0.5-4.0 $\AA$')
        ax[1].set(yscale='log', ylim=[10 ** -9, 10 ** -2])
        ax[1].set_yticks([10 ** -8, 10 ** -7, 10 ** -6, 10 ** -5, 10 ** -4, 10 ** -3])
        for a in ax:
            for t in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
                a.axvline(date_time_obj.replace(minute=0, second=0, microsecond=0) + timedelta(hours=t),
                          color="grey", ls="dashed", lw=0.5)
            a.set_xlim(date_time_obj, date_time_obj + timedelta(hours=23, minutes=59, seconds=59))
            a.tick_params(which="both", direction="in")
        ax[1].xaxis.set_major_locator(dates.HourLocator(interval=2))
        ax[1].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
        ax[1].legend(frameon=True, loc='upper center', ncol=2)
        # Create GOES Class interval bands.
        ax2 = ax[1].twinx()
        ax2.set(yscale='log', ylim=[10 ** -9, 10 ** -2])
        ax2.set_yticks([3 * 10 ** -8, 3 * 10 ** -7, 3 * 10 ** -6, 3 * 10 ** -5, 3 * 10 ** -4])
        for band in [1 * 10 ** -8, 1 * 10 ** -7, 1 * 10 ** -6, 1 * 10 ** -5, 1 * 10 ** -4, 1 * 10 ** -3]:
            ax2.axhline(band, color="grey", ls="dashed", lw=1)
        ax2.set_yticklabels(['A', 'B', 'C', 'M', 'X'], fontsize=12)
        ax2.tick_params(axis=u'both', which=u'both', length=0)
        # Create axis and plot labels.
        ax[0].set_ylabel("Signal strength (dB)")
        ax[1].set_ylabel("Flux (Wm$^{-2}$)")
        ax[1].set_xlabel("Time: {:s} (UTC)".format(date_time_obj.strftime("%Y-%m-%d")))
        ax[0].set_title('SuperSID (' + header['Site'] + ', ' + header['Country'] + ') - ' +
                        header['StationID'] + ' (' + transmitters[header['StationID']][2] +
                        ', ' + header['Frequency'][0:-3] + '.' + header['Frequency'][2] +
                        'kHz' + ')')
        # Configure image dimensions.
        plt.subplots_adjust(hspace=0.01)
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 500 / float(dpi))
        fig.tight_layout()
        # Save figure to the archive.
        parent = Path(config_archive) / header['Site'].lower() / date_time_obj.strftime('%Y/%m/%d') / 'png'
        image_path = parent / file_path.split('/')[-1][:-4]
        if not parent.exists():
            parent.mkdir(parents=True)
        fig.savefig(fname=image_path)
        plt.close()
        return Path(str(image_path) + '.png')

    def create_plot(self, header, data, file_path):
        """
        Generate plot for given parameters and data.

        Parameters
        ----------
        header : dict
            Dictionary containing observation parameters, eg. transmitter freq.
        data : object
            Pandas dataframe containing csv data.
        file_path : str
            Path to csv file.

        Returns
        -------
        image_path : str
            Path to image location.
        """
        fig, ax = plt.subplots(1, figsize=(9, 3))
        # Get local sunrise and sunset markers.
        geo = Geographic_Midpoint()
        date_time_obj = datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S')
        try:
            sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), 53.33, 6.25)
            ax.axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Local Sunrise')
            ax.axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Local Sunset')
        except ValueError:
            print("Sun is always above the horizon on this day, at this location.")
        # Plot VLF data.
        sid = pd.Series(data['signal_strength'].values, index=pd.to_datetime(data['datetime']))
        ax.plot(sid, color='k')
        ax.xaxis.set_major_locator(dates.HourLocator(interval=2))
        ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
        for t in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            ax.axvline(date_time_obj.replace(minute=0, second=0, microsecond=0) + timedelta(hours=t),
                       color="grey", ls="dashed", lw=0.5)
        ax.set_xlim(date_time_obj, date_time_obj + timedelta(hours=23, minutes=59, seconds=59))
        ax.tick_params(which="both", direction="in")
        # Display time generated.
        ax.text(0.875, 0.03, 'Generated : ' + datetime.utcnow().strftime('%d-%b-%y %H:%M') + ' UTC',
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
                fontsize=8)
        # Create axis and plot labels.
        ax.set_ylabel("Signal strength (dB)")
        ax.set_ylabel("Flux (Wm$^{-2}$)")
        ax.set_xlabel("Time: {:s} (UTC)".format(date_time_obj.strftime("%Y-%m-%d")))
        ax.set_title('SuperSID (' + header['Site'] + ', ' + header['Country'] + ') - ' +
                     header['StationID'] + ' (' + transmitters[header['StationID']][2] +
                     ', ' + header['Frequency'][0:-3] + '.' + header['Frequency'][2] +
                     'kHz' + ')')
        # Configure image dimensions.
        plt.subplots_adjust(hspace=0.01)
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 400 / float(dpi))
        fig.tight_layout()
        # Save figure to the archive.
        parent = Path(config_archive) / header['Site'].lower() / date_time_obj.strftime('%Y/%m/%d') / 'png'
        image_path = parent / file_path.split('/')[-1][:-4]
        if not parent.exists():
            parent.mkdir(parents=True)
        fig.savefig(fname=image_path)
        plt.close()
        return Path(str(image_path) + '.png')
