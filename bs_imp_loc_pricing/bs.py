# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 21:21:27 2019

@author: Perry
"""

# Black Scholes Basics

import math
import numpy as np
import pandas as pd
import scipy.interpolate as scipl
from scipy.stats import norm

def rtcv(curve, key):
    return np.interp(key, g_rate['tenor'].to_list(), g_rate[curve].to_list())
   
def bs_npv_analytical_std(s,vol,k,t,quote,r,q=0,cat='c'):
    cat = cat.lower()[:1]
    t = t/365
    vol = vol/100
    r = r/100
    q = q/100
    d1 = (math.log(s/k) + (r-q+0.5*vol*vol)*t) / (vol*math.sqrt(t))
    d2 = d1 - vol*math.sqrt(t)
    if cat == 'c':
        return s*math.exp(-q*t)*norm.cdf(d1) - k*math.exp(-r*t)*norm.cdf(d2)
    elif cat == 'p':
        return k*math.exp(-r*t)*norm.cdf(-d2) - s*math.exp(-q*t)*norm.cdf(-d1) 
    else:
        raise ValueError('undefined option type')

def bs_delta_analytical_std(s,vol,k,t,quote,r,q=0,cat='c'):
    cat = cat.lower()[:1]
    t = t/365
    vol = vol/100
    r = r/100
    q = q/100
    d1 = (math.log(s/k) + (r-q+0.5*vol*vol)*t) / (vol*math.sqrt(t))
    if cat == 'c':
        return math.exp(-q*t)*norm.cdf(d1)
    elif cat == 'p':
        return -math.exp(-q*t)*norm.cdf(-d1) 
    else:
        raise ValueError('undefined option type')

def bs_gamma_analytical_std(s,vol,k,t,quote,r,q=0,cat='c'):
    cat = cat.lower()[:1]
    t = t/365
    vol = vol/100
    r = r/100
    q = q/100
    d1 = (math.log(s/k) + (r-q+0.5*vol*vol)*t) / (vol*math.sqrt(t))
    if cat == 'c' or cat == 'p':
        return math.exp(-q*t)*norm.pdf(d1)/(s*vol*math.sqrt(t))
    else:
        raise ValueError('undefined option type')

def bs_vega_analytical_std(s,vol,k,t,quote,r,q=0,cat='c'):
    cat = cat.lower()[:1]
    t = t/365
    vol = vol/100
    r = r/100
    q = q/100
    d1 = (math.log(s/k) + (r-q+0.5*vol*vol)*t) / (vol*math.sqrt(t))
    if cat == 'c' or cat == 'p':
        return s*math.exp(-q*t)*norm.pdf(d1)*math.sqrt(t)
    else:
        raise ValueError('undefined option type')

def bs_impvol_analytical_std(it = 100, **kwarg):
    kwarg['vol'] = 25
    for i in range(it):
        kwarg['vol'] -= 100*(bs_npv_analytical_std(**kwarg) - kwarg['quote'])/bs_vega_analytical_std(**kwarg)
    return kwarg['vol']

def bs_impvol_interpl(k,t,volsurface):
    return ()

def dupire_locvol_extrapl(k,t,s,volsurface):
    iv = bs_impvol_interpl(k,t,volsurface)
    dt = 1
    dk = 0.01
    r = rtcv('r',t)
    q = rtcv('q',t)
    div_dt = (bs_impvol_interpl(k,t+dt,volsurface) - bs_impvol_interpl(k,t-dt,volsurface))/(2*dt)
    div_dk = (bs_impvol_interpl(k+dk,t,volsurface) - bs_impvol_interpl(k-dk,t,volsurface))/(2*dk)
    div2_dk2 = (bs_impvol_interpl(k+dk,t,volsurface) + bs_impvol_interpl(k-dk,t,volsurface) 
                - 2*bs_impvol_interpl(k-dk,t,volsurface))/(4*dk*dk)
    return (iv*iv + 2*iv*t*(div_dt + (r-q)*k*div_dk))\
            /((1 - k*math.log(k/(g_spot*math.exp(r*t-q*t)))*div_dk)**2 + k*iv*t*(div_dk - 1/4*k*div*t*div_dk**2 + k*div2_dk2))

op1 = {'s':38.9,'vol':21.92,'k':37.25,'t':105.0,'r':2.22,'cat':'p','quote':1.9}
#npv_op1 = bs_npv_analytical_std(**op1)
impvol = bs_impvol_analytical_std(**op1)
#delta_op1 = bs_delta_analytical_std(**op1)
#gamma_op1 = bs_gamma_analytical_std(**op1)
#vega_op1 = bs_vega_analytical_std(**op1)/100