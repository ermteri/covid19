#!/usr/bin/env python3

import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import requests
import sys

ECDC_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'


class CovidStats:
    def __init__(self):
        self.csv_url = ECDC_URL
        # fields = ['dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'countriesAndTerritories', 'geoId',
        #          'countryterritoryCode', 'popData2018', 'continentExp']

    def moving_average(self, a, n=3):
        ret = np.cumsum(a, dtype=int)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def get_csv(self):
        req = requests.get(self.csv_url)
        return csv.DictReader(req.text.splitlines())

    def print_graph(self, csv_reader):
        fig = plt.subplots()
        x = list()
        d = list()
        c = list()
        for row in csv_reader:
            date_time_obj = datetime.datetime.strptime(row['dateRep'], '%d/%m/%Y')
            x.append(date_time_obj)
            c.append(int(row['cases']))
            d.append(int(row['deaths']))
        plt.xticks(rotation=90)
        plt.grid()
        plt.plot(x[:len(x)-6], self.moving_average(c, 7), label='cases')
        plt.plot(x[:len(x)-6], self.moving_average(d, 7), label='deaths')
        plt.title('Moving 7-days average')
        plt.legend(loc='best')
        plt.show()


def run(args):
    cs = CovidStats()
    sweden = (row for row in cs.get_csv() if row['countriesAndTerritories'] == 'Sweden')
    cs.print_graph(sweden)


if __name__ == '__main__':
    run(sys.argv)

