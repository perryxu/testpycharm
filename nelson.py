# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 10:13:38 2020

@author: Perry Xu
"""

import numpy as np
import QuantLib as ql
import pandas as pd
import datetime
import matplotlib.pyplot as plt

xls_bond = pd.ExcelFile('E:\Learning\Quantlib Python\CGB20200220.xls')
df_bond = xls_bond.parse('Sheet1')

def dt_tau(d1,d2):
    return (d2-d1).days/365

def dt_to_qldate(d):
    return ql.Date(d.day, d.month, d.year)

def sche_gen(arr):
    if arr['CPN_FREQ'] == 1:
        return ql.Schedule(dt_to_qldate(arr['ISSDATE']),
                           dt_to_qldate(arr['MATURITY']),
                           ql.Period(12, ql.Months), ql.China(),
                           ql.Following, ql.Following,
                           ql.DateGeneration.Backward, False)
    elif arr['CPN_FREQ'] == 2:
        return ql.Schedule(dt_to_qldate(arr['ISSDATE']),
                   dt_to_qldate(arr['MATURITY']),
                   ql.Period(6, ql.Months), ql.China(),
                   ql.Following, ql.Following,
                   ql.DateGeneration.Backward, False)

def bondhelper_gen(arr):
    return ql.BondHelper(ql.QuoteHandle(ql.SimpleQuote(arr['CPRICE'])),
                            ql.FixedRateBond(1, 100.0, sche_gen(arr), [arr['COUPON_PCT']/100], ql.Actual365Fixed()))
    
today = ql.Date(20, 2, 2020)
ql.Settings.instance().evaluationDate = today
df_bond['MATURITY'] = pd.to_datetime(df_bond['MATURITY']).dt.date
df_bond['HDATE'] = pd.to_datetime(df_bond['HDATE']).dt.date
df_bond['ISSDATE'] = pd.to_datetime(df_bond['ISSDATE']).dt.date
df_bond = df_bond[df_bond['MATURITY'] < datetime.date(2030,12,31)]
df_bond['BONDHELPER'] = df_bond.apply(bondhelper_gen, axis=1)
bondhelpers = list(df_bond['BONDHELPER'])

curve_fix_method = ql.SvenssonFitting()
fit_tolerance = 1.0e-8
fit_iteration = 10000

bond_fit_ns = ql.FittedBondDiscountCurve(1, ql.China(), bondhelpers,
                                          ql.Actual365Fixed(), 
                                          curve_fix_method, fit_tolerance, fit_iteration)
res = bond_fit_ns.fitResults()


plt.title('CDCC Bond Yield Curve - CGB')
ttm = [i/4 for i in range(0,10*4)]
plt.plot(ttm, [bond_fit_ns.zeroRate(t, ql.Simple).rate()*100 for t in ttm], label = 'nelson-siegel')
plt.plot([dt_tau(datetime.date(2020,2,20), t) for t in df_bond['MATURITY']], list(df_bond['YLDMKT']), 'o')
plt.show()




#
# 
#terminationDates = [ql.Date(4, 7, 2044), ql.Date(15, 2, 2028), ql.Date(14, 4, 2023)]
#tenors = np.repeat(ql.Period(ql.Annual), 3) #allusion on R function rep()
#calenders = np.repeat(ql.Germany(), 3)
#termDateConvs = np.repeat(ql.Following, 3)
#genRules = np.repeat(ql.DateGeneration.Backward, 3)
#endOfMonths = np.repeat(False, 3)
#firstDates = [ql.Date(27, 4, 2012), ql.Date(10, 1, 2018), ql.Date(2, 2, 2018)]
# 
#settlementDays = np.repeat(2, 3)
#coupons = [0.025, 0.005, 0.0]
#cleanPrices = [126.18, 98.18, 99.73]
#faceValues = np.repeat(100.0, 3)
#dayCounts = np.repeat(ql.ActualActual(), 3)
# 
#schedules = []
#bonds = []
#bondHelpers = []
#for j in range(0, 3):
#    # without int() and bool() conversion it will not work due to int vs. int32_ and bool vs bool_
#    schedules.append(ql.Schedule(firstDates[j], terminationDates[j], tenors[j], calenders[j],
#                                 int(termDateConvs[j]), int(termDateConvs[j]), int(genRules[j]),
#                                 bool(endOfMonths[j])))
#    bonds.append(ql.FixedRateBond(int(settlementDays[j]), float(faceValues[j]), schedules[j],
#                                  [float(coupons[j])], dayCounts[j]))
#    bondHelpers.append(ql.BondHelper(ql.QuoteHandle(ql.SimpleQuote(float(cleanPrices[j]))), bonds[j]))
# 
#list(schedules[0])
#list(schedules[1])
#list(schedules[2])
# 
#print(bonds[0].bondYield(float(cleanPrices[0]), dayCounts[0], ql.Compounded, ql.Annual))
#print(bonds[1].bondYield(float(cleanPrices[1]), dayCounts[1], ql.Compounded, ql.Annual))
#print(bonds[2].bondYield(float(cleanPrices[2]), dayCounts[2], ql.Compounded, ql.Annual))
# 
#curveSettlementDays = 2
#curveCalendar = ql.Germany()
#curveDaycounter = ql.ActualActual()
# 
##piecewise log cubic discount curve. Surprisingly there is no log-linear...
#yieldCurve = ql.PiecewiseLogCubicDiscount(today, bondHelpers, curveDaycounter)
#print(yieldCurve.discount(ql.Date(1, 3, 2019)))
#print(yieldCurve.discount(ql.Date(1, 3, 2020)))
#print(yieldCurve.discount(ql.Date(1, 3, 2035)))
# 
###and Nelson-Siegel
#curveFittingMethod = ql.NelsonSiegelFitting()
#tolerance = 1.0e-5
#iterations = 1000
#yieldCurveNS = ql.FittedBondDiscountCurve(curveSettlementDays, curveCalendar, bondHelpers,
#                                          curveDaycounter, curveFittingMethod, tolerance, iterations)
#res = yieldCurveNS.fitResults()
#print(yieldCurveNS.discount(ql.Date(1, 3, 2019)))
#print(yieldCurveNS.discount(ql.Date(1, 3, 2020)))
#print(yieldCurveNS.discount(ql.Date(1, 3, 2035)))