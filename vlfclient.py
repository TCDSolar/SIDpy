"""
Client containing functions specific to the processing of SuperSID VLF data; 
reading csv files, get data from csv, get header information from csv, 
normalize data, convert data to pandas dataframe, plot data and create summary
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

from geographic_midpoint import Geographic_Midpoint
from read_config import config_data
from vlf_transmitter_dict import transmitters


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

        fig, ax1 = plt.subplots(figsize=(6.4, 4.8))
        ax1.set(xlabel='Start Time: ' + time[0].strftime('%Y-%m-%d %H:%M:%S'),
                ylabel='Amplitude (dB)',
                title=parameters['Site'] + '_' + parameters['StationID'] +
                      time[0].strftime('_%Y-%m-%d_%H:%M:%S'))
        ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))
        ax1.plot(time, signal)
        geo = Geographic_Midpoint()
        date_time_obj = datetime.strptime(parameters['UTC_StartTime'],
                                          '%Y-%m-%d%H:%M:%S')
        latlon = geo.calc_midpoint([float(parameters['Latitude']),
                                    float(parameters['Longitude'])],
                                   transmitters[parameters['StationID']])
        sunrise, sunset = geo.sunrise_sunset(date_time_obj.date(), latlon[0],
                                             latlon[1])
        ax1.axvspan(sunrise - timedelta(hours=1), sunrise + timedelta(hours=1),
                    alpha=0.5, color='orange', label='Sunrise')
        ax1.axvspan(sunset - timedelta(hours=1), sunset + timedelta(hours=1),
                    alpha=0.5, color='red', label='Sunset')
        ax1.legend()
        dpi = fig.get_dpi()
        fig.set_size_inches(1000 / float(dpi), 500 / float(dpi))
        image_path = (config_data + "/" + file_path[len(config_data) + 1:-4])
        fig.savefig(fname=image_path)
        plt.close()
        return Path(str(image_path) + '.png')

    def get_recent_goes(self):
        """
        Pull the most recent GOES X-ray data from the NOAA page
        
        Returns the GOES short and long channels as pandas series
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
        
        """
        tstart = datetime(2020, 11, 8, 00, 00)

        dunsink = []
        birr = []
        for file in os.listdir('temp'):
            dataframe = self.read_csv('temp/' + file)
            header, data = self.get_header(dataframe), self.get_data(dataframe)
            if 'Dunsink' in file:
                dunsink.append([header, data])
            else:
                birr.append([header, data])
        gl, gs = self.get_recent_goes()

        fig, ax = plt.subplots(1, sharex=True, figsize=(9, 12))
        colours = ['y', 'b', 'g', 'r', 'c', 'm']

        # plot the VLF data
        for transmitter, c in zip(dunsink, colours):
            sid = pd.Series(transmitter[1]['signal_strength'].values,
                            index=pd.to_datetime(transmitter[1]['datetime']))
            ax[0].plot(sid, label=transmitter[0]['StationID'], color=c)
        ax[0].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
        ax[0].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

        """
        for transmitter, c in zip(birr, colours):
            sid = pd.Series(transmitter[1]['signal_strength'].values,
            index=pd.to_datetime(transmitter[1]['datetime']))
            ax[2].plot(sid, label=transmitter[0]['StationID'], color=c)
        ax[2].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
        ax[2].legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
        
        # plot the GOES data
        ax[1].plot(gl, color='r')
        ax[1].plot(gs, color='b')
        ax[1].set(yscale='log', ylim=[10 ** -9, 10 ** -2])
        """

        times = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

        for a in ax:
            for t in times:
                a.axvline(tstart + timedelta(hours=t),
                          color="grey", ls="dashed")
            a.tick_params(which="both", direction="in")

        ax[0].set_ylabel("Dunsink signal strength (dB)")
        # ax[2].set_ylabel("Birr signal strength (dB)")
        # ax[1].set_ylabel("Flux Wm$^{-2}$")
        # ax[1].set_xlabel("Time " + tstart.strftime("%m/%d/%Y"))

        # ax[1].set_xlim(tstart, tend)
        # ax[1].xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.01)

        plt.savefig("data/summary/" + file[:-4], dpi=200)
