#!/usr/bin/env python3

import argparse
import csv
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import requests
import sys
from collections import defaultdict

ECDC_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
# URL above use these fields =
# ['dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'countriesAndTerritories',
# 'geoId', 'countryterritoryCode', 'popData2018', 'continentExp']


class CovidStats:
    def __init__(self):
        self.csv_url = ECDC_URL

    def get_csv(self):
        req = requests.get(self.csv_url)
        return csv.DictReader(req.text.splitlines())

    def moving_average(self, a, n=3):
        ret = np.cumsum(a, dtype=int)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def get_ecdc_data(self, countries, kind):
        '''
        Fetches csv data from ECDC
        :return:
        {"country1":[12, 13, 1, 0]}
        '''
        csv_reader = self.get_csv()
        result = defaultdict(list)
        found = list()
        # Reversed since in the csv from ECDC, latest is first in the list
        for line in reversed(list(csv_reader)):
            if line['countriesAndTerritories'] in countries:
                if int(line[kind]) > 0:
                    found.append(line['countriesAndTerritories'])
                if line['countriesAndTerritories'] in found:
                    if line['countriesAndTerritories'] in result:
                        result[line['countriesAndTerritories']].append(int(line[kind])/int(line['popData2018'])*1000000)
                    else:
                        result[line['countriesAndTerritories']] = [int(line[kind])/int(line['popData2018'])*1000000]
        return result

    def plot(self, data, kind):
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        fig, y_ax = plt.subplots()
        y_ax.set_xlabel('Days')
        y_ax.set_ylabel(kind, color='tab:blue')
        y_ax.tick_params(axis='y', labelcolor='tab:blue')
        y_ax.tick_params(axis='x', rotation=90)

        # Reversed since in the csv from ECDC, latest is first in the list
        i = 0
        for country in data:
            trend_color = colors[i]
            i = i + 1
            y_ax.plot(self.moving_average(data[country], 7), color=trend_color, label=country)
        plt.title('Moving average of {} per 1 million (from 1st {})'.format(kind, kind))
        y_ax.legend(loc='upper left')
        fig.tight_layout()
        plt.show()


def run(args):
    parser = argparse.ArgumentParser(description='Compares corona trends for a selected countries.')
    parser.add_argument('-c', '--countries', nargs='+', metavar='S', required=True, help='Countries in question')
    parser.add_argument('-k', '--kind', type=str, required=True, help="Kind of graph, deaths or cases")
    args = parser.parse_args()
    cs = CovidStats()
    data = cs.get_ecdc_data(args.countries, args.kind)
    # print(json.dumps(data, indent=4))
    cs.plot(data, args.kind)


if __name__ == '__main__':
    run(sys.argv)

