'''
(c) 2017 Red Tech Research Corporation
This source code is released under the New BSD license.  Please see

Created on November 2017

@author: Romeo Demeterio
@contact: romeodemeteriojr@gmail.com
@summary: Event Profiler Tutorial
'''


import numpy as np
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess_v02 as da
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, d_data, price):
    ''' Finding the event dataframe '''
    print "Finding Events"

    df_close = d_data['actual_close']

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the prices for this timestamp
            f_sym_act_price_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_sym_act_price_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol was greater/equal to $5 the previous day
            # and is lesser than $5 on the current day
            if f_sym_act_price_today < float(price) and f_sym_act_price_yest >= float(price):
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

def profile_pricedrop_event(dt_start, dt_end, s_symbols_file, price=5):
    '''
    TODO:
    :param dt_start:
    :param dt_end:
    :param s_symbols_file:
    :param price:
    :return:
    '''
    print "--------------------------------------------------------------------------------------------------------------"
    print "Profiling " +  s_symbols_file + " at price $" + str(float(price)) + " from " + str(dt_start) + " to " + str(dt_end)
    print "--------------------------------------------------------------------------------------------------------------"
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(s_symbols_file)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data, price)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename= "price_" + str(price) + "_" +s_symbols_file + '.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')



if __name__ == '__main__':
    """
    Main function
    """
    #1
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008")
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012")

    #2, 7
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", 6)
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", 6)

    #3, 8
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", 7)
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", 7)

    #4, 9
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", 8)
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", 8)

    #5, 10
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", 9)
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", 9)

    #6, 11
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", 10)
    profile_pricedrop_event(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", 10)
