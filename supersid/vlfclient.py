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

from supersid.config.config import data_path as config_data, archive_path as config_archive, transmitters
from supersid.geographic_midpoint.geographic_midpoint import Geographic_Midpoint


class VLFClient:
    """
    """

    def read_csv(self, filename):
        """
        Read .csv files contianing signal strength and time.

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

    def get_header(self, df):
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

    def norm_data(self, df):
        """
        Takes pandas dataframe and normalizes signal strength intensity.

        Parameters
        ----------
        df : object
            Pandas dataframe containing csv data.

        Returns
        -------
        df : object
            Pandas dataframe containing normalized csv data.
        """
        df['signal_strength'] = ((df['signal_strength'] -
                                  df['signal_strength'].min()) / (df['signal_strength'].max() -
                                                                  df['signal_strength'].min()))
        return df

    def db_data(self, df):
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

    def create_plot(self, parameters, data, file_path):
        """
        Generate plot for given parameters and data.

        Parameters
        ----------
        parameters : dict
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
        time, signal = data.datetime.tolist(), data.signal_strength.tolist()

        fig, ax1 = plt.subplots(figsize=(9, 3))
        ax1.set(xlabel='Time: (UTC)',
                ylabel='Signal Strength (dB)',
                title='SuperSID (' + parameters['Site'] + ', ' +
                      parameters['Country'] + ') - ' +
                      parameters['StationID'] + ' (' +
                      transmitters[parameters['StationID']][2] +
                      ', ' + parameters['Frequency'][0:-3] + '.' + parameters['Frequency'][2] + 'kHz' + ')')
        ax1.xaxis.set_major_locator(dates.HourLocator(interval=2))
        ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax1.plot(time, signal, color='k')

        geo = Geographic_Midpoint()
        date_time_obj = datetime.strptime(parameters['UTC_StartTime'],
                                          '%Y-%m-%d%H:%M:%S')
        try:
            sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), 53.33, 6.25)
            ax1.axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Dunsink Sunrise')
            ax1.axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Dunsink Sunset')
        except ValueError:
            print("Sun is always above the horizon on this day, at this location.")
        t_start = date_time_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        t_end = date_time_obj.replace(hour=23, minute=59, second=59, microsecond=59)
        ax1.set_xlim(t_start, t_end)
        for t in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            ax1.axvline(t_start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=t),
                        color="grey", ls="dashed", lw=0.5)
        ax1.text(0.88, 0.03, 'Generated : ' + datetime.utcnow().strftime('%d-%b-%y %H:%M') + ' UTC',
                 horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes,
                 fontsize=8)
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 500 / float(dpi))
        image_path = (config_data + "/" + file_path[len(config_data) + 1:-4])
        fig.tight_layout()
        fig.savefig(fname=image_path)
        plt.close()
        return Path(str(image_path) + '.png')

    def get_recent_goes(self):
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

    def summary_plot(self):
        """
        Create summary plot of all data for specified site. This is currently
        a Work In Progress (WIP).

        Returns
        -------

        """

        for file in os.listdir(config_data):
            if file.endswith('.csv') and not file.__contains__("current") and not file.__contains__(" "):
                dataframe = self.read_csv(config_data + '/' + file)
                header, data = self.get_header(dataframe), self.get_data(dataframe)

                gl, gs = self.get_recent_goes()
                fig, ax = plt.subplots(2, sharex=True, figsize=(9, 6))

                t_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
                t_end = t_start.replace(hour=23, minute=59, second=59)

                geo = Geographic_Midpoint()
                date_time_obj = datetime.strptime(header['UTC_StartTime'],
                                                  '%Y-%m-%d%H:%M:%S')
                try:
                    sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), 53.33, 6.25)
                    ax[0].axvline(sunrise, alpha=0.5, ls="dashed", color='orange', label='Dunsink Sunrise')
                    ax[0].axvline(sunset, alpha=0.5, ls="dashed", color='red', label='Dunsink Sunset')
                except ValueError:
                    print("Sun is always above the horizon on this day, at this location.")

                sid = pd.Series(data['signal_strength'].values,
                                index=pd.to_datetime(data['datetime']))
                ax[0].plot(sid, color='k')

                ax[0].xaxis.set_major_locator(dates.HourLocator(interval=2))
                ax[0].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
                ax[1].text(0.875, 0.03, 'Generated : ' + datetime.utcnow().strftime('%d-%b-%y %H:%M') + ' UTC',
                           horizontalalignment='center', verticalalignment='center', transform=ax[1].transAxes,
                           fontsize=8)

                ax[1].plot(gl, color='r', label='GOES 1.0-8.0 $\AA$')
                ax[1].plot(gs, color='b', label='GOES 0.5-4.0 $\AA$')
                ax[1].set(yscale='log', ylim=[10 ** -9, 10 ** -2])
                ax[1].set_yticks([10 ** -8, 10 ** -7, 10 ** -6, 10 ** -5, 10 ** -4, 10 ** -3])

                for a in ax:
                    for t in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
                        a.axvline(t_start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=t),
                                  color="grey", ls="dashed", lw=0.5)
                    a.set_xlim(t_start, t_end)
                    a.tick_params(which="both", direction="in")

                ax[0].set_ylabel("Signal strength (dB)")
                ax[1].set_ylabel("Flux (Wm$^{-2}$)")
                ax[1].set_xlabel("Time: (UTC)")

                ax[1].xaxis.set_major_locator(dates.HourLocator(interval=2))
                ax[1].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))

                ax2 = ax[1].twinx()
                ax2.set(yscale='log', ylim=[10 ** -9, 10 ** -2])
                ax2.set_yticks([3 * 10 ** -8, 3 * 10 ** -7, 3 * 10 ** -6, 3 * 10 ** -5, 3 * 10 ** -4])
                for band in [1 * 10 ** -8, 1 * 10 ** -7, 1 * 10 ** -6, 1 * 10 ** -5, 1 * 10 ** -4, 1 * 10 ** -3]:
                    ax2.axhline(band, color="grey", ls="dashed", lw=1)
                ax2.set_yticklabels(['A', 'B', 'C', 'M', 'X'], fontsize=12)
                ax2.tick_params(axis=u'both', which=u'both', length=0)

                ax[0].set_title(
                    'SuperSID (' + header['Site'] + ', ' + header['Country'] + ') - ' + header['StationID'] + ' (' +
                    transmitters[header['StationID']][2] + ', ' + header['Frequency'][0:-3] +'.' + header['Frequency'][2] + 'kHz' + ')')

                ax[1].legend(frameon=True, loc='upper center', ncol=2)

                fig.tight_layout()
                plt.subplots_adjust(hspace=0.01)

                if 'Dunsink' in file:
                    summary_path = config_archive + '/dunsink/live/' + header['StationID']
                else:
                    summary_path = config_archive + '/birr/live/' + header['StationID']

                plt.savefig(summary_path, dpi=200)
