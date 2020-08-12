#!/usr/bin/env python3

import argparse
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import requests
import sys

ECDC_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
# URL above use these fields =
# ['dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'countriesAndTerritories',
# 'geoId', 'countryterritoryCode', 'popData2019', 'continentExp']


class CovidStats:
    def __init__(self):
        self.csv_url = ECDC_URL

    def moving_average(self, a, n=3):
        ret = np.cumsum(a, dtype=int)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def get_csv(self):
        req = requests.get(self.csv_url)
        return csv.DictReader(req.text.splitlines())

    def plot_one(self, country, csv_reader, kind, use_population):
        x = list()
        y = list()
        first_found = False
        # Reversed since in the csv from ECDC, latest is first in the list
        for row in reversed(list(csv_reader)):
            if not first_found:
                if int(row[kind]) == 0:
                    continue
                else:
                    first_found = True
            date_time_obj = datetime.datetime.strptime(row['dateRep'], '%d/%m/%Y')
            x.append(date_time_obj)
            if use_population:
                y.append(int(row[kind])/int(row['popData2019'])*1000000)
            else:
                y.append(int(row[kind]))
        fig, y_ax = plt.subplots()
        trend_color = 'darkblue'
        bar_color = 'tab:blue'
        y_ax.set_xlabel('Date (s)')
        y_ax.set_ylabel(kind, color=bar_color)
        y_ax.plot(x[6:], self.moving_average(y, 7), '--', color=trend_color, label='7 day moving average')
        y_ax.bar(x, y, color=bar_color)
        y_ax.tick_params(axis='y', labelcolor=bar_color)
        y_ax.tick_params(axis='x', rotation=90)
        if use_population:
            plt.title('Number of {} per 1 million in {} (from 1st {})'.format(kind, country, kind))
        else:
            plt.title('Number of {} in {} (from 1st {})'.format(kind, country, kind))
        y_ax.legend(loc='upper left')
        fig.tight_layout()
        plt.show()


def run(args):
    parser = argparse.ArgumentParser(description='Show corona stats for a selected country.')
    parser.add_argument('-c', '--country', type=str, required=True, help='Country in question')
    parser.add_argument('-k', '--kind', type=str, required=True, help="Kind of graph, deaths or cases")
    parser.add_argument('-p', '--population', action='store_true', default=False,
                        help="Compare relative to population")
    args = parser.parse_args()
    cs = CovidStats()
    csv_reader = cs.get_csv()
    country = (row for row in csv_reader if row['countriesAndTerritories'] == args.country)
    cs.plot_one(args.country, country, args.kind, args.population)


if __name__ == '__main__':
    run(sys.argv)

