from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.tools import yahoofinance
from pyalgotrade import plotter
import subprocess
from pyalgotrade.technical import bollinger
import sys, os, time
import operator
#import Control_interface

g_strongIndex_discount = 0.15 
g_weakIndex_discount = 0.10
g_overSoldThreshold = 20 
g_overBoughThreshold = 50
bBandsPeriod = 16
buying_stock = {}
earning_stock = {}

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed,companyID,smaPeriod, rsiPeriod, invest_amount):
        strategy.BacktestingStrategy.__init__(self, feed, invest_amount)
        self.__sma = ma.SMA(feed.getDataSeries(companyID).getCloseDataSeries(), smaPeriod)
        self.__sma60 = ma.SMA(feed.getDataSeries(companyID).getCloseDataSeries(), 60)
	self.__sma90 = ma.SMA(feed.getDataSeries(companyID).getCloseDataSeries(), 90)
	self.__rsi = rsi.RSI(feed.getDataSeries(companyID).getCloseDataSeries(), rsiPeriod)
	self.__bbands = bollinger.BollingerBands(feed[companyID].getCloseDataSeries(), bBandsPeriod, 2)
        self.__position = None
        self.__boxFloor = 1000
	self.__boxCeiling = 0
	self.__cmpID = companyID
	self.__amount = invest_amount
	self.__strengthIndex = None
	self.__discount = None
	self.__fee = 0
        self.__lastStatus = False
	self.__cross_lower = 0
        self.__buyin_price = 0
     	
    def getBollingerBands(self):
        return self.__bbands
    def onStart(self):
        print "Initial portfolio value: $%.2f" % self.getBroker().getCash()

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        print "%s: BUY at $%.2f" % (execInfo.getDateTime(), execInfo.getPrice())

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        print "%s: SELL at $%.2f" % (execInfo.getDateTime(), execInfo.getPrice())
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.exitPosition(self.__position)

    def onBars(self, bars):
	bar = bars.getBar(self.__cmpID)
	lower = self.__bbands.getLowerBand()[-1]
	upper = self.__bbands.getUpperBand()[-1]
	mid = self.__bbands.getMiddleBand()[-1]
     
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
	    # calculate box floor and box ceiling
	    if bar.getClose() > self.__boxCeiling:
                self.__boxCeiling = bar.getClose()
            if bar.getClose() < self.__boxFloor:
                self.__boxFloor = bar.getClose()
	    if(lower >= bar.getClose() and self.__cross_lower == 1):
		 self.__cross_lower=0
	    if(lower < bar.getClose() and self.__cross_lower == 0):
		 self.__cross_lower=1
            return
	# calculate yearly strength 
	if (self.__boxFloor and self.__boxCeiling and self.__sma[-1]):
            # change the algorithm here
	    if (self.__sma[-1] < 0.618*(self.__boxFloor + self.__boxCeiling) and self.__sma[-1] > 0.382*(self.__boxFloor + self.__boxCeiling)):	
	    	self.__strengthIndex = 1
		self.__discount = g_strongIndex_discount
	    else:
		self.__strengthIndex = 0
		self.__discount = g_weakIndex_discount
	    #print self.__cmpID, " 's strength number is ", self.__strengthIndex 

        # If a position was not opened, check if we should enter a long position.
        if self.__position == None:
            #print "cur_price = ", bar.getClose()
            #print "cur_average = ", self.__sma50[-1]
            #print "cur_variation = ", (bar.getHigh() - bar.getLow())/bar.getClose()
            #print (float(bar.getClose())/0.9 < upper)
            #print "bar.getClose() = ", bar.getClose()
            #print "upper = ", upper 
           # if (((bar.getClose() > self.__sma[-1] and (float(bar.getClose())/0.9 < upper)) or (float(bar.getClose()) > float(bar.getLow() + bar.getHigh())/2)) and (bar.getHigh() - bar.getLow())/bar.getClose() > 0.05):    # strategy 1
             if ((bar.getClose() < self.__sma[-1] and bar.getClose() < mid) or (self.__sma[-1] > self.__sma60[-1] and self.__sma60[-1] > self.__sma90[-1] and bar.getClose()/(1-self.__discount) > mid and self.__rsi[-1] < g_overBoughThreshold) or ((bar.getClose() < lower or (bar.getClose() > mid)) and self.__sma[-1] > self.__sma60[-1])):  # strategy 2
		# Buying max shares
                if(bar.getClose() != 0):
			share_can_buy = self.__amount/bar.getClose()
                else:
			share_can_buy = 5000

                # Enter a buy market order for 10 orcl shares. The order is good till canceled.
                self.__buyin_price = bar.getClose()		
		self.__position = self.enterLong(self.__cmpID, share_can_buy, True)
                self.lastStatus = True
		print "Average curve = ", self.__sma[-1]
        # Check if we have to exit the position.
        elif ((bar.getClose() > self.__sma[-1]*(1 + g_strongIndex_discount)) or (bar.getClose() > upper and self.__buyin_price*1.10 < upper) or (bar.getClose() < lower and lower < self.__buyin_price*0.92) or (bar.getClose() < self.__buyin_price*0.9)):
	     #upper = self.__bbands.getUpperBand()[-1]
	     if(bar.getClose() > mid or bar.getClose() < lower): 
             	self.exitPosition(self.__position)
	     	print "Average curve = ", self.__sma[-1]
             	self.lastStatus = False
	     	self.__fee = self.__fee + 20

    def onFinish(self, bars):
        bar = bars.getBar(self.__cmpID)
        print "Final portfolio value: $%.2f" % self.getBroker().getValue()
	print "Average curve = ", self.__sma[-1]
	print "transaction fee = ", self.__fee
        print "earning = ", self.getBroker().getValue() - self.__fee
        #global earning_stock
        #earning_stock[self.__cmpID] = self.getBroker().getValue() - self.__fee
        if((self.__rsi[-1] < g_overSoldThreshold or self.__rsi[-1] > g_overBoughThreshold) and bar.getClose() > 15):
#or (bar.getClose() > self.__sma200[-1] and self.__rsi[-1] <= g_overSoldThreshold))):
#or (bar.getClose() > self.__sma200[-1] and self.__rsi[-1] <= g_overSoldThreshold)):
                global buying_stock
        	buying_stock[self.__cmpID] = self.__sma[-1]
        if((self.__sma[-1] > self.__sma60[-1] and self.__sma60[-1] > self.__sma90[-1]) and bar.getClose() > 15):
		global earning_stock
		earning_stock[self.__cmpID] = self.__sma[-1]
	        #if(self.getBroker().getValue() - self.__fee > 5000):
		#	global earning_stock
		#	earning_stock[self.__cmpID] = self.getBroker().getValue() - self.__fee
			




