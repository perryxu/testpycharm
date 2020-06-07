# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 00:06:26 2020

@author: Perry Xu
"""

import math
import utils
import pandas as pd
from QuantLib import *

today = Date(17, 4, 2020)
Settings.instance().evaluationDate = today
china_cal = China()

helpers = [ DepositRateHelper(QuoteHandle(SimpleQuote(rate/100)),
                              Period(3, Months), fixingDays,
                              china_cal, Following, False, Actual365Fixed())
            for rate, fixingDays in [(4.15, 1)] ]

shibor = Shibor(Period(3, Months))

helpers += [ SwapRateHelper(QuoteHandle(SimpleQuote(rate/100)), 
                            Period(*tenor), china_cal, Quarterly, ModifiedFollowing,
                            Actual365Fixed(), shibor, QuoteHandle(), Period(1, Days))
             for rate, tenor in [(4.04, (6, Months)), (4.0337, (9, Months)),
                                 (4.0725, (1, Years)), (4.0725, (2, Years)),
                                (4.0825,(3, Years)), (4.0550,(4, Years)),
                                (4.1000,(5, Years))] ]

# We let the reference date of the curve move with the global evaluation date, 
# by specifying it as '0' days after the latter on the TARGET calendar. 


# cubic - zero
# linear - zero
# logcubic - discount
# flat - forward - ins
# linear - forward - ins


#lpr1y_curve_cubic_zero = PiecewiseCubicZero(0, china_cal, helpers, Actual365Fixed())
lpr1y_curve_cubic_zero = PiecewiseCubicZero(today, helpers, Actual365Fixed())
lpr1y_curve_linear_zero = PiecewiseLinearZero(today, helpers, Actual365Fixed())
lpr1y_curve_logcubic_discount = PiecewiseLogCubicDiscount(today, helpers, Actual365Fixed())
lpr1y_curve_flat_forward = PiecewiseFlatForward(today, helpers, Actual365Fixed())
lpr1y_curve_cubic_zero.enableExtrapolation()
lpr1y_curve_linear_zero.enableExtrapolation()
lpr1y_curve_logcubic_discount.enableExtrapolation()
lpr1y_curve_flat_forward.enableExtrapolation()

# zerocurve的node就是zero curve， discount curve 的node就是discount factor
#lpr1y_nodes = lpr1y_curve.nodes()
#temp_dates, temp_rates = zip(*lpr1y_nodes)
# jump是在原curve基础上扰动
# ForwardCurve只能构建flatforward的模式
#temp_curve = ForwardCurve(temp_dates, temp_rates,
#                          lpr1y_curve.dayCounter())


dates = [ Date(d) for d in range(today.serialNumber(),(today+Period(4, Years)).serialNumber()) ]
#rates_fwd_1d = [ lpr1y_curve.forwardRate(d, TARGET().advance(d,1,Days),Actual365Fixed(), Simple).rate()
#                    for d in dates ]
#temp_fwd_1d = [ temp_curve.forwardRate(d, TARGET().advance(d,1,Days),Actual365Fixed(), Simple).rate()
#                    for d in dates ]
zr_cubic_zero = [lpr1y_curve_cubic_zero.zeroRate(d, Actual365Fixed(), Continuous).rate() for d in dates]
zr_linear_zero = [lpr1y_curve_linear_zero.zeroRate(d, Actual365Fixed(), Continuous).rate() for d in dates]
zr_logcubic_disc = [lpr1y_curve_logcubic_discount.zeroRate(d, Actual365Fixed(), Continuous).rate() for d in dates]
zr_flat_fwd = [lpr1y_curve_flat_forward.zeroRate(d, Actual365Fixed(), Continuous).rate() for d in dates]

period = (3, Months)
fr3m_cubic_zero = [ lpr1y_curve_cubic_zero.forwardRate(d, TARGET().advance(d,*period),Actual365Fixed(), Simple).rate() for d in dates ]
fr3m_linear_zero = [ lpr1y_curve_linear_zero.forwardRate(d, TARGET().advance(d,*period),Actual365Fixed(), Simple).rate() for d in dates ]
fr3m_logcubic_disc = [ lpr1y_curve_logcubic_discount.forwardRate(d, TARGET().advance(d,*period),Actual365Fixed(), Simple).rate() for d in dates ]
fr3m_flat_fwd = [ lpr1y_curve_flat_forward.forwardRate(d, TARGET().advance(d,*period),Actual365Fixed(), Simple).rate() for d in dates ]

#df_fwdrate = pd.DataFrame(data={'DATE':dates, 'FWD3M':rates_fwd_1d, 'ZERO':rates_zero})
#df_fwdrate['GAP'] = df_fwdrate['DATE'] - df_fwdrate.at[0,'DATE']
#df_fwdrate['ZERO_CHECK'] = df_fwdrate['ZERO'] - df_fwdrate['ZERO'].shift(1)

#_, ax = utils.plot()
#utils.highlight_x_axis(ax)
#utils.plot_curve(ax, dates, [(rates_zero,'-')], format_rates=True)
#utils.plot_curve(ax, dates, [(rates_zero,'-')], format_rates=True)
#utils.plot_curve(ax, dates, [(temp_fwd_1d,'-')], format_rates=True)
#ax.set_ylim(0.039,0.042)

import datetime
# dates = [ datetime.date(d.year(), d.month(), d.dayOfMonth()) for d in dates]
dates = [ (d - dates[0])/365 for d in dates]

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#plt.rcParams['savefig.dpi'] = 100
#plt.rcParams['figure.dpi'] = 100
plt.title('LPR Curve with Various Interpolation - Zero Rates')

plt.plot(dates, fr3m_cubic_zero, label = 'cubic interpolated on zero rate')
plt.plot(dates, fr3m_linear_zero, label = 'linear interpolated on zero rate')
plt.plot(dates, fr3m_logcubic_disc, label = 'logcubic interpolated on discount factor')
plt.plot(dates, fr3m_flat_fwd, label = 'flat interpolated on fwd rate')
plt.xlabel('Maturity')
plt.ylabel('Zero Rate - Countinuously Compounded')
plt.legend()
plt.show()
