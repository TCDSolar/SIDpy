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

import logging
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import dates
from sunpy.time import parse_time

from sidpy.config.config import transmitters
from sidpy.geographic_midpoint.geographic_midpoint import Geographic_Midpoint
from scipy.signal import savgol_filter

np.seterr(divide='ignore')
pd.options.mode.chained_assignment = None


class VLFClient:
    """
    Client containing functions specific to the processing of SuperSID VLF data;
    reading csv files, get data from csv, get header information from csv,
    normalize data, convert data to pandas DataFrame, plot data and create summary
    plot.
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
        logging.debug('File %s read.', filename)
        return df

    @staticmethod
    def get_data(df, original_sid):
        """
        Generate new dataframe containing only datetime and signal
        intensity with comments removed.

        Parameters
        ----------
        df : object
            Pandas dataframe containing csv data.
        original_sid : bool
            Statement on whether SID or Supersid data is being used.

        Returns
        -------
        df : object
            Pandas dataframe containing normalized csv data without comments.
        """
        df = df[~df['datetime'].astype(str).str.startswith('#')]
        try:
            df['datetime'] = pd.to_datetime(df['datetime'],
                                            format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            df['datetime'] = pd.to_datetime(df['datetime'],
                                            format='%Y-%m-%d %H:%M:%S.%f')

        if original_sid == False:
            df['signal_strength'] = pd.to_numeric(df['signal_strength'])
            df['signal_strength'] = savgol_filter(df['signal_strength'], 9, 1)
            df['signal_strength'] = 20 * np.log10(df['signal_strength'])
        logging.debug('File data obtained.')
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
        logging.debug('File header obtained.')
        return parameters_dict

    @staticmethod
    def get_recent_goes(file="https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json"):
        """
        Process GOES XRS files defaults to most recent GOES X-ray data from the NOAA page.

        Returns
        -------
        gl : pd.DataFrame object
                The GOES long channels as pandas series
        gs : pd.DataFrame object
                The GOES short channels as pandas series
        """
        try:
            data = pd.read_json(file)
            logging.debug('GOES swpc xrays-7-day data acquired.')
            data_short = data[data["energy"] == "0.05-0.4nm"]
            data_long = data[data["energy"] == "0.1-0.8nm"]
            time_array = [parse_time(x).datetime for x in
                          data_short['time_tag'].values]

            gl = pd.Series(data_long["flux"].values, index=time_array)
            gs = pd.Series(data_short["flux"].values, index=time_array)
            logging.debug('GOES XRS data processed.')
            return gl, gs
        except Exception:
            return None, None

    @staticmethod
    def create_plot_xrs(header, data, file_path, archive_path, gl, gs, original_sid=False):
        """
        Generate plot for given parameters and data.

        Parameters
        ----------
        header : dict
            Dictionary containing observation parameters, eg. transmitter freq.
        data : object
            Pandas dataframe containing csv data.
        file_path : PosixPath
            Path to archive.
        archive_path : PosixPath
            Path to csv file.
        gl : pandas.Series
            GOES XRS Long data.
        gs : pandas.Series
            GOES XRS Short data.
        original_sid : bool
            Statement on whether SID or Supersid data is being used.


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
            sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), header['Latitude'], header['Longitude'])
            ax[0].axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Local Sunrise')
            ax[0].axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Local Sunset')
        except ValueError:
            logging.warning("Sun is always above the horizon on this day, at this location.")
        # Plot VLF data.
        sid = pd.Series(data['signal_strength'].values, index=pd.to_datetime(data['datetime']))
        if date_time_obj.date() == datetime.utcnow().date():
            sid.sort_index()
            sid = sid.truncate(after=datetime.utcnow().replace(minute=0, second=0) - timedelta(seconds=20))
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
        ax[1].set_ylabel("Flux (Wm$^{-2}$)")
        ax[1].set_xlabel("Time: {:s} (UTC)".format(date_time_obj.strftime("%Y-%m-%d")))
        if original_sid == True:
            ax[0].set_ylabel("Volts (V)")
            ax[0].set_title('SID (' + header['Site'] + ') - ' + header['StationID'] + ' (' +
                            transmitters[str(header['StationID'])][2] + ', ' + header['Frequency'][0:-3] +
                            '.' + header['Frequency'][2] + 'kHz' + ')')
            parent = (Path(archive_path) / header['Site'].lower() / 'sid' /
                      date_time_obj.strftime('%Y') / date_time_obj.strftime('%m') /
                      date_time_obj.strftime('%d') / 'png')
        else:
            ax[0].set_ylabel("Signal Strength (dB)")
            ax[0].set_title('SuperSID (' + header['Site'] + ', ' + header['Country'] + ') - ' +
                            header['StationID'] + ' (' + transmitters[str(header['StationID'])][2] +
                            ', ' + header['Frequency'][0:-3] + ' kHz' + ')')
            parent = (Path(archive_path) / header['Site'].lower() / 'super_sid' /
                      date_time_obj.strftime('%Y') / date_time_obj.strftime('%m') /
                      date_time_obj.strftime('%d') / 'png')
        # Configure image dimensions.
        plt.subplots_adjust(hspace=0.01)
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 500 / float(dpi))
        fig.tight_layout()
        # Save figure to the archive.
        image_path = (parent / file_path.name).with_suffix('.png')
        if not parent.exists():
            parent.mkdir(parents=True)
        fig.savefig(fname=image_path)
        plt.close()
        logging.debug('%s generated', image_path.name)
        return image_path

    @staticmethod
    def create_plot(header, data, file_path, archive_path, original_sid=False):
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
        archive_path : str
            Path to archive.
        original_sid : bool
            Statement on whether SID or Supersid data is being used.

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
            sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), header['Latitude'], header['Longitude'])
            ax.axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Local Sunrise')
            ax.axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Local Sunset')
        except ValueError:
            logging.warning("Sun is always above the horizon on this day, at this location.")
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
        ax.set_xlabel("Time: {:s} (UTC)".format(date_time_obj.strftime("%Y-%m-%d")))
        if original_sid == True:
            ax.set_ylabel("Volts (V)")
            ax.set_title('SID (' + header['Site'] + ') - ' + header['StationID'] + ' (' +
                         transmitters[header['StationID']][2] + ', ' + header['Frequency'][0:-3] +
                         '.' + header['Frequency'][2] + 'kHz' + ')')
            parent = (Path(archive_path) / header['Site'].lower() / 'sid' /
                      date_time_obj.strftime('%Y') / date_time_obj.strftime('%m') /
                      date_time_obj.strftime('%d') / 'png')
        else:
            ax.set_ylabel("Signal Strength (dB)")
            ax.set_title('SuperSID (' + header['Site'] + ', ' + header['Country'] + ') - ' +
                         header['StationID'] + ' (' + transmitters[header['StationID']][2] +
                         ', ' + header['Frequency'][0:-3] + ' kHz' + ')')
            parent = (Path(archive_path) / header['Site'].lower() / 'super_sid' /
                      date_time_obj.strftime('%Y') / date_time_obj.strftime('%m') /
                      date_time_obj.strftime('%d') / 'png')
        # Configure image dimensions.
        plt.subplots_adjust(hspace=0.01)
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 400 / float(dpi))
        fig.tight_layout()
        # Save figure to the archive.
        image_path = (parent / file_path.name).with_suffix('.png')
        if not parent.exists():
            parent.mkdir(parents=True)
        fig.savefig(fname=image_path)
        plt.close()
        logging.debug('%s generated', (image_path.name))
        return image_path
