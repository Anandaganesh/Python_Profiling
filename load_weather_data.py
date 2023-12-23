"""This program downloads the weather data for the specified stations
and calculates low and high weather for the given year"""

import csv
import sys
import requests
import collections
from statistics import mean


# This function downloads the weather data for station/year and write the output as a csv file
def download_weather_station_data(station, year):
    my_url = generic_url.format(station=station, year=year)
    req = requests.get(my_url)
    if req.status_code != 200:
        return

    with open(generic_file.format(station=station, year=year), 'w') as sf:
        sf.write(req.text)


# This parent function downloads the weather data for the given station list and year range
def download_all_weather_station_data(stations_list, start_year, end_year):
    for station in stations_list:
        for year in range(start_year, end_year + 1):
            download_weather_station_data(station, year)


# This function gets the temperature details from the file
def get_file_temperature(file_name):
    with open(file_name, 'r') as tf:
        reader = csv.reader(tf)
        header = next(reader)

        for row in reader:
            station = row[header.index("STATION")]
            temp = row[header.index("TMP")]
            temperature, status = temp.split(",")
            if int(status) != 1:
                continue
            temperature = int(temperature) / 10

            yield temperature


# This parent function gets all the temperatures for the given station and year
def get_temperatures_all(stations_list, start_year, end_year):
    temperatures = collections.defaultdict(list)
    for station in stations_list:
        for year in range(start_year, end_year + 1):
            for temperature in get_file_temperature(generic_file.format(station=station, year=year)):
                temperatures[station].append(temperature)
    return temperatures


# This function gets the maximum/minimum/average temperature for the station over the given years
def get_temperatures(lst_temperatures, calc_mode):
    result = {}
    for mode in calc_mode:
        if mode == 'max':
            result[mode] = {station: max(temperatures) for station, temperatures in lst_temperatures.items()}
        elif mode == 'min':
            result[mode] = {station: min(temperatures) for station, temperatures in lst_temperatures.items()}
        else:
            result[mode] = {station: mean(temperatures) for station, temperatures in lst_temperatures.items()}
    return result


# Main Function
if __name__ := "__main__":
    stations = sys.argv[1].split(",")
    years = [int(year) for year in sys.argv[2].split("-")]
    first_year = years[0]
    last_year = years[1]

    generic_url = "https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station}.csv"
    generic_file = "Weather_station_{station}_{year}.csv"

    download_all_weather_station_data(stations, first_year, last_year)
    temperatures_all = get_temperatures_all(stations, first_year, last_year)
    temperatures_values = get_temperatures(temperatures_all, ['max', 'min', 'avg'])

    print(f"The temperatures are {temperatures_values}")
