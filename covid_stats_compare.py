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

    def get_ecdc_data_total(self, countries, kind, use_population):
        '''
        Fetches csv data from ECDC from 2019-12-31
        :return:
        {"country1":[12, 13, 1, 0]}
        '''
        csv_reader = self.get_csv()
        result = defaultdict(list)
        # Reversed since in the csv from ECDC, latest is first in the list
        for line in reversed(list(csv_reader)):
            if line['countriesAndTerritories'] in countries:
                if line['countriesAndTerritories'] in result:
                    if use_population:
                        result[line['countriesAndTerritories']].append(int(line[kind])/int(line['popData2018'])*1000000)
                    else:
                        result[line['countriesAndTerritories']].append(int(line[kind]))
                else:
                    if use_population:
                        result[line['countriesAndTerritories']] = [int(line[kind]) / int(line['popData2018']) * 1000000]
                    else:
                        result[line['countriesAndTerritories']] = [int(line[kind])]
        return result

    def get_ecdc_data(self, countries, kind, use_population):
        '''
        Fetches csv data from ECDC from 1 case
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
                        if use_population:
                            result[line['countriesAndTerritories']].append(int(line[kind])/int(line['popData2018'])*1000000)
                        else:
                            result[line['countriesAndTerritories']].append(int(line[kind]))
                    else:
                        if use_population:
                            result[line['countriesAndTerritories']] = [int(line[kind])/int(line['popData2018'])*1000000]
                        else:
                            result[line['countriesAndTerritories']] = [int(line[kind])]
        return result

    def plot(self, data, kind, use_population, total):
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
        if total:
            from_part = '2019-12-31'
        else:
            from_part = '1st {}'.format(kind)
        if use_population:
            plt.title('7 days Moving average of {}/million (from {})'.format(kind, from_part))
        else:
            plt.title('7 days Moving average of {} (from {})'.format(kind, from_part))
        y_ax.legend(loc='upper left')
        fig.tight_layout()
        plt.show()


def run(args):
    parser = argparse.ArgumentParser(description='Compares corona trends for a selected countries.')
    parser.add_argument('-c', '--countries', nargs='+', metavar='S', required=True,
                        help='Countries in question')
    parser.add_argument('-k', '--kind', type=str, required=True,
                        help="Kind of graph, deaths or cases")
    parser.add_argument('-p', '--population', action='store_true', default=False,
                        help="Compare relative to population")
    parser.add_argument('-t', '--total', action='store_true', default=False,
                        help="If total data from 2019-12-31 should be used")

    args = parser.parse_args()
    cs = CovidStats()
    if args.total:
        data = cs.get_ecdc_data_total(args.countries, args.kind, args.population)
    else:
        data = cs.get_ecdc_data(args.countries, args.kind, args.population)
    # print(json.dumps(data, indent=4))
    cs.plot(data, args.kind, args.population, args.total)


if __name__ == '__main__':
    run(sys.argv)

