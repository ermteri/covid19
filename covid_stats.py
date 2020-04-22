#!/usr/bin/env python3

import argparse
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
        plt.plot(x[6:], self.moving_average(c, 7), label='cases')
        plt.plot(x[6:], self.moving_average(d, 7), label='deaths')
        plt.title('Moving 7-days average')
        plt.legend(loc='best')
        plt.show()

    def plot(self, country, csv_reader):
        date_list = list()
        death_list = list()
        cases_list = list()
        for row in csv_reader:
            date_time_obj = datetime.datetime.strptime(row['dateRep'], '%d/%m/%Y')
            date_list.append(date_time_obj)
            cases_list.append(int(row['cases']))
            death_list.append(int(row['deaths']))

        fig, cases = plt.subplots()
        # create the first y-axis
        color = 'tab:blue'
        cases.set_xlabel('Date (s)')
        cases.set_ylabel('Cases', color=color)
        cases.plot(date_list[:-6], self.moving_average(cases_list, 7), color=color)
        cases.tick_params(axis='y', labelcolor=color)
        cases.tick_params(axis='x', rotation=90)
        # Create a second y-axis
        death = cases.twinx()
        color = 'tab:red'
        death.set_ylabel('Death', color=color)
        death.plot(date_list[:-6], self.moving_average(death_list, 7), color=color)
        death.tick_params(axis='y', labelcolor=color)
        # Show the plot
        plt.title('Moving 7-days average for ' +  country)
        fig.tight_layout()
        plt.show()


def run(args):
    parser = argparse.ArgumentParser(description='Show corona stats moving ave 7 days.')
    parser.add_argument('-c', '--country', type=str, required=True, help='the country in question')
    args = parser.parse_args()
    cs = CovidStats()
    print(args.country)
    csv_reader = cs.get_csv()
    country = (row for row in csv_reader if row['countriesAndTerritories'] == args.country)
    cs.plot(args.country, country)


if __name__ == '__main__':
    run(sys.argv)

