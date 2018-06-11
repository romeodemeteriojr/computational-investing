'''
(c) 2017 Red Tech Research Corporation
This source code is released under the New BSD license.  Please see

Created on November 2017

@author: Romeo Demeterio
@contact: romeodemeteriojr@gmail.com
@summary: Very crude portfolio optimizer. Needs optimization...(get it, get it)? Only works with 4 stocks for now.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import pandas as pd
import numpy as np
import math as math
import matplotlib.pyplot as plt

print "Pandas Version", pd.__version__


def simulate(dt_start, dt_end, ls_port_symbols, lf_port_alloc, b_chartify=False):
    """
    Simulate portfolio performance
    :param dt_start:
    :param dt_end:
    :param ls_port_symbols:
    :param lf_port_alloc:
    :param chartify:
    :return:
    """

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source. No cache.
    # c_dataobj = da.DataAccess("Yahoo", cachestalltime=0)
    c_dataobj = da.DataAccess("Yahoo")

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_port_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Copy the normalized prices to a new ndarray to find returns.
    na_rets = na_normalized_price.copy()

    # Estimate portfolio returns
    # Multiply each column by the allocation to the corresponding equity
    na_port_rets = na_rets * lf_port_alloc

    # Sum each row for each day. That is your Fund Investment.
    na_port_rets_sum = np.sum(na_port_rets, axis=1)

    # Divide each daily return by first return. That is your cumulative daily portfolio value.
    # na_port_rets_cum = na_port_rets_sum / na_port_rets_sum[0]
    # port_rets_cum = na_port_rets_cum[-1]
    port_rets_cum = na_port_rets_sum[-1] / na_port_rets_sum[0]
    # print "Cumulative Return: ", port_rets_cum

    # Get daily return
    na_port_rets_daily = na_port_rets_sum.copy()
    tsu.returnize0(na_port_rets_daily)

    # Get daily return average
    port_rets_daily_avg = np.mean(na_port_rets_daily)
    # print "Average Daily Return: ", port_rets_daily_avg

    # Get daily return volatility
    port_rets_daily_std = np.std(na_port_rets_daily)
    # print "Volatility: ", port_rets_daily_std

    # Get portfolio Sharpe ratio
    port_sharpe_ratio = math.sqrt(252) * port_rets_daily_avg / port_rets_daily_std
    # print "Sharpe Ratio: ", port_sharpe_ratio

    if b_chartify:
        chartify(ls_port_symbols, ldt_timestamps, na_rets, na_port_rets_sum)

    return (port_rets_cum, port_rets_daily_avg, port_rets_daily_std, port_sharpe_ratio)


def chartify(ls_port_symbols, ldt_timestamps, na_rets, na_port_rets_sum):
    """
    Create chart of portofolio vs components and/or another stock i.e. SPY
    :param na_rets:
    :param na_port_rets_sum:
    :return:
    """
    # Plotting the results
    font = {'family': 'normal',
            'weight': 'normal',
            'size': 5}
    plt.rc('font', **font)
    plt.clf()
    fig = plt.figure()
    fig.add_subplot(111)
    plt.plot(ldt_timestamps, na_rets, alpha=0.4)
    plt.plot(ldt_timestamps, na_port_rets_sum)
    ls_names = ls_port_symbols
    ls_names.append('Portfolio')
    plt.legend(ls_names)
    plt.ylabel('Cumulative Returns')
    plt.xlabel('Date')
    fig.autofmt_xdate(rotation=45)
    plt.savefig('optimizer_v01.pdf', format='pdf')


def main():
    ''' Main Function'''

    # List of portfolio symbols
    # ls_port_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
    # ls_port_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    # ls_port_symbols = ["AAPL", "GLD"]

    # ls_port_symbols = ["AAPL", "GOOG", "IBM", "MSFT"] # Q1
    # ls_port_symbols = ['BRCM', 'ADBE', 'AMD', 'ADI']  # Q2
    # ls_port_symbols = ['BRCM', 'TXN', 'AMD', 'ADI']   # Q3
    # ls_port_symbols = ['BRCM', 'TXN', 'IBM', 'HNZ']   # Q4
    # ls_port_symbols = ['C', 'GS', 'IBM', 'HNZ']       # Q5
    ls_port_symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT'] # Q6
    # ls_port_symbols = ['BRCM', 'ADBE', 'AMD', 'ADI']  # Q7
    # ls_port_symbols = ['BRCM', 'TXN', 'AMD', 'ADI']   # Q8
    # ls_port_symbols = ['BRCM', 'TXN', 'IBM', 'HNZ']   # Q9
    # ls_port_symbols = ['C', 'GS', 'IBM', 'HNZ']       # Q10


    # simulation start date
    dt_start = dt.datetime(2003, 1, 1)
    # simulation end date
    dt_end = dt.datetime(2011, 12, 31)

    # list of legal allocations in 0.1 increments.
    alloc_10_inc = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    optimal_alloc = [0.0, 0.0, 0.0, 0.0]
    optimal_sharpe = 0

    for aloc1 in alloc_10_inc:
        for aloc2 in alloc_10_inc:
            for aloc3 in alloc_10_inc:
                for aloc4 in alloc_10_inc:
                    if (aloc1 + aloc2 + aloc3 + aloc4 == 1):
                        ls_port_alloc = [aloc1, aloc2, aloc3, aloc4]
                        cum_ret, daily_ret, vol, sharpe = simulate(dt_start, dt_end, ls_port_symbols, ls_port_alloc)
                        if (sharpe > optimal_sharpe):
                            optimal_sharpe = sharpe
                            optimal_alloc = ls_port_alloc
                            print "Highest Sharpe: ", optimal_sharpe
                            print "New Optimal Allocations: ", optimal_alloc
                        else:
                            print "Not optimal: ", sharpe

    cum_ret, daily_ret, vol, sharpe = simulate(dt_start, dt_end, ls_port_symbols, optimal_alloc)

    print
    print
    print "-------------------------------------------------"
    print "Start Date: ", dt_start
    print "End Date: ", dt_end
    print "Symbols: ", ls_port_symbols
    print "Optimal Allocations: ", optimal_alloc
    print "Sharpe Ratio: ", sharpe
    print "Volatility (stdev of daily returns): ", vol
    print "Average Daily Return: ", daily_ret
    print "Cumulative Return: ", cum_ret
    print "-------------------------------------------------"

    # Let's include market benchmark shall we....and chart it against our portfolio
    ls_port_symbols.append("NDAQ")
    optimal_alloc.append(0.0)
    simulate(dt_start, dt_end, ls_port_symbols, optimal_alloc, True)


if __name__ == '__main__':
    main()
