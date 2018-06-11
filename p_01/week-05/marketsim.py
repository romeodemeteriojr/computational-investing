'''
(c) 2017 Red Tech Research Corporation
This source code is released under the New BSD license.  Please see

Created on November 2017

@author: Romeo Demeterio
@contact: romeodemeteriojr@gmail.com
@summary: Market Simulator
'''
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import csv
import numpy as np
import pandas as pa
import dateutil.parser as dp
import os
import datetime as dt
from sys import argv


class Order(object):
    BUY = "Buy"
    SELL = "Sell"


def check_filepath(s_fpath):
    if (os.path.exists(s_fpath)):
        return s_fpath

    print "Did not find path to " + s_fpath
    return None


def read_orders(s_fpath):
    '''
    Read CSV into "trades" array
    :param s_fpath:
    :return: orders array
    '''
    a_symbols = []
    a_dates = []
    a_orders = []
    np_orders = None
    csv_file = check_filepath(s_fpath)
    try:
        if csv_file != None:
            csv_file = open(s_fpath, 'rU')
            reader = csv.reader(csv_file, delimiter=',')

            # reader each row
            for row in reader:
                # TODO: add date checking i.e. try/catch
                temp_date = dp.parse(row[0] + '-' + row[1] + '-' + row[2])
                if not (temp_date in a_dates):
                    a_dates.append(temp_date)
                if not (row[3] in a_symbols):
                    a_symbols.append(row[3])
                a_orders.append([temp_date, row[3], row[4], row[5]])

            # Sort dates and symbols
            a_symbols.sort()
            a_dates.sort()
            a_orders.sort()

            # Numpyrize csv orders
            np_orders = np.array(a_orders)
    except:
        print "Error in reading " + s_fpath

    # remove duplicates in symbols and date arrays (but no duplicates already)
    # a_symbols = list(set(a_symbols))
    # a_dates = list(set(a_dates))

    return (a_symbols, a_dates, np_orders)


def pull_histo_data(dt_start, dt_end, ls_symbols, source='Yahoo'):
    '''
    Read stock data from source
    :param dt_start:
    :param dt_end:
    :param ls_symbols:
    :return:
    '''
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    # ldt_timestamps = du.getNYSEdays(dt_start, dt_end)

    # Creating an object of the dataaccess class. No cache.
    # c_dataobj = da.DataAccess("Yahoo", cachestalltime=0)
    c_dataobj = da.DataAccess(source)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_histo_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    df_histo_data = dict(zip(ls_keys, ldf_histo_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        df_histo_data[s_key] = df_histo_data[s_key].fillna(method='ffill')
        df_histo_data[s_key] = df_histo_data[s_key].fillna(method='bfill')
        df_histo_data[s_key] = df_histo_data[s_key].fillna(1.0)

    return df_histo_data


def make_order_matrix(df_adj_price, np_orders):
    '''
    * Create a dataframe which has all values as zero with index as dates and columns as symbols.
    * Iterate the orders array and fill the number of shares for that particular symbol and date.
    * Remember: Sell is same as buying negative shares.
    :param df_adj_price:
    :param np_orders:
    :return:
    '''
    # TODO: Validate arguments
    # Create order matrix and set all values to zero
    df_order_matrix = df_adj_price.copy()
    df_order_matrix[:] = 0.0
    # Iterate the orders array and fill the number of shares for that particular symbol and date.
    for order in np_orders:
        # print (order)
        date = order[0] + dt.timedelta(hours=16)
        if order[2] == Order.SELL:
            df_order_matrix[order[1]].ix[date] = df_order_matrix[order[1]].ix[date] - float(order[3])
        else:
            df_order_matrix[order[1]].ix[date] = df_order_matrix[order[1]].ix[date] + float(order[3])

    return df_order_matrix


def calculate_fund(np_orders, df_adj_price, df_portf):
    '''
    Scan orders and update portfolio data frame.
    :param np_orders: 
    :param df_adj_price: 
    :param df_portf: 
    :return: 
    '''
    # TODO: validate arguments

    # Scan each order
    # for order in np_orders:
    # Check if order date is


# Scan trades to create ownership array and value

# Scan cash and value to create total fund value

if __name__ == '__main__':
    _, n_fund, f_orders, f_values = argv

    # print ("Starting fund:", n_fund)
    # print ("Orders file:", f_orders)
    # print ("Values file:", f_values)

    ###############################################
    # Read the dates and symbols
    ###############################################
    order_symbols, order_dates, np_orders = read_orders(f_orders)

    # print order_symbols
    # print order_dates
    # print np_orders

    ###############################################
    # Read the historical data
    ###############################################
    # offset end date with one day to read the close of the last date

    dt_end = order_dates[-1] + du.timedelta(days=1)
    df_histo_data = pull_histo_data(order_dates[0], dt_end, order_symbols)

    # Prices data frame
    df_adj_price = df_histo_data['close']

    ###############################################
    # Create order matrix, the matrix of shares
    ###############################################
    df_shares_matrix = make_order_matrix(df_adj_price, np_orders)

    ###############################################
    # Calculate the cash time series
    ###############################################
    # Unnecessary step?

    ###############################################
    # Calculate the cash timeseries
    ###############################################

    # Make holdings matrix from shares matrix (very easy with python)
    df_holdings_matrix = -df_shares_matrix * df_adj_price

    # Add cash column in shares matrix
    df_holdings_matrix['IO_CASH'] = 0.0
    # Add the rows to have total share value of day
    df_holdings_matrix['IO_CASH'] = df_holdings_matrix.sum(axis=1)

    # set first date with initial cash + value of shares
    dt_start = order_dates[0] + dt.timedelta(hours=16)
    #df_holdings_matrix['IO_CASH'].ix[dt_start] = df_holdings_matrix['IO_CASH'].ix[dt_start] + float(n_fund)

    # Get cumulative value of fund
    df_holdings_matrix['FUND'] = 0.0
    #df_holdings_matrix['FUND'].ix[dt_start] = float(n_fund)
    df_holdings_matrix['FUND'] = df_holdings_matrix['IO_CASH'].cumsum()

    print df_holdings_matrix

    # Write to CSV
