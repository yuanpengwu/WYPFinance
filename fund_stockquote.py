#!/bin/python

import sys
import ystockquote
import urllib

eps_limit = 0.1

def eps_threshold(symbol):
	cur_eps = ystockquote.get_eps(symbol)
   	if('N/A' == cur_eps):
		return True
   	elif(float(cur_eps) >= eps_limit):
		return True
   	else:
		return False

def get_price(symbol):
	cur_price = ystockquote.get_previous_close(symbol)
	if('N/A' == cur_price):
		return 0.1
	else:
		return cur_price

def get_volume(symbol):
	return ystockquote.get_volume(symbol)

def get_average_volume(symbol):
        cur_volume = ystockquote.get_average_daily_volume(symbol)
        if ('N/A' == cur_volume):
		return 1
	return cur_volume

def get_eps(symbol):
	cur_eps = ystockquote.get_eps(symbol)
        if('N/A' == cur_eps):
		return 0.0
	else:
		return cur_eps
def get_pe(symbol):
	cur_pe = ystockquote.get_pe(symbol)
	if('N/A' == cur_pe):
		return 0.0
	else:
		return cur_pe
def get_todays_high(symbol):
	cur_price = ystockquote.get_todays_high(symbol)
        if('N/A' == cur_price):
                return 0.1
        else:
                return cur_price
def get_todays_low(symbol):
	cur_price = ystockquote.get_todays_low(symbol)
        if('N/A' == cur_price):
                return 0.1
        else:
                return cur_price


