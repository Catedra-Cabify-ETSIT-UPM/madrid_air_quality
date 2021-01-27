#!/usr/bin/env python3

# Python script with functions to manipulate air quality
# data from datos.madrid.es. It is meant to be imported as
# a library.

import pandas as pd
import numpy as np


def pollutant_daily_ts(path, station_code, pollutant):
    """Return the daily time series of a pollutant measssured
    at a station.
    
    Arguments:
        path (str): path to the csv file
        station_code (int): station code (e.g. 28079035)
        pollutant (int): pollutant code (e.g. 8)
        
    Returns:
        pandas.core.series.Series: daily time series
    """
    # Split and format the station code
    station_code = str(station_code)
    province = int(station_code[:2])
    municipality = int(station_code[2:5])
    station = int(station_code[5:9])
    
    # Read and filter the original CSV
    aq = pd.read_csv(path, sep=';').query("PROVINCIA == @province & " \
                                          "MUNICIPIO == @municipality & " \
                                          "ESTACION == @station & " \
                                          "MAGNITUD == @pollutant"
                                         ).filter(regex=("D\d\d|ANO|MES"))
    
    # Melt the DataFrame from (months x days) to (DateTime x columns)
    aq_melted = aq.melt(id_vars=['ANO', 'MES'], var_name='day',
                         value_name='pollutant').sort_values(by=['MES', 'day'])
    aq_melted.index = pd.to_datetime(dict(
        year=aq_melted['ANO'],
        month=aq_melted['MES'],
        day=aq_melted['day'].str[1:].astype(int)
    ), errors='coerce')
    
    # Get the pollutant time series
    ts = aq_melted['pollutant'].replace(0, np.nan)
    
    return ts


def pollutant_daily_ts_several(paths, station_code, pollutant):
    """Return the daily time series of a pollutant measssured
    at a station of several years
    
    Arguments:
        paths (list): tuplke of paths to the csv files
        station_code (int): station code (e.g. 28079035)
        pollutant (int): pollutant code (e.g. 8)
        
    Returns:
        pandas.core.series.Series: daily time series
    """
    series = []
    
    for p in paths:
        series.append(pollutant_daily_ts(p, station_code, pollutant))
        
    return pd.concat(series).sort_index()
    