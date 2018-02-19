from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.tools import yahoofinance
from pyalgotrade import plotter
import subprocess
from pyalgotrade.technical import bollinger
import sys, os, time, datetime, re
import operator
from old_strategy import MyStrategy
import old_strategy
import sendMail
import fund_stockquote




def run_strategy(smaPeriod, rsiPeriod, instrument, amount, plot):
    # Load the yahoo feed from the CSV file
    try:
        feed = yahoofinance.build_feed([instrument], 2014, 2015, "/home/pwu/stock/database")
    except:
        print "can't download..."
        pass
    else:
    # Evaluate the strategy with the feed's bars.
        myStrategy = MyStrategy(feed, instrument, smaPeriod, rsiPeriod, amount)
        if plot:
                plt = plotter.StrategyPlotter(myStrategy, True, True, True)
                plt.getInstrumentSubplot(instrument).addDataSeries("upper", myStrategy.getBollingerBands().getUpperBand())
                plt.getInstrumentSubplot(instrument).addDataSeries("middle", myStrategy.getBollingerBands().getMiddleBand())
                plt.getInstrumentSubplot(instrument).addDataSeries("lower", myStrategy.getBollingerBands().getLowerBand())
        myStrategy.run()
        if plot:
                plt.plot()



# mainRoutine
investLen = 28
rsiLen = 15
#companyNameSign = "cyou"
amount = 5000
# whether the overall state has changed?
state = 0
#earning_stock = {}
#buying_stock = {}
list_name = 'nasdaq.list'
#list_name = 'core.list'
#line = "cyou"
g_changing_range = 0.08
prv_time = time.time()
initial_flag = False
email_file="/home/pwu/stock/trading_result.txt"
margin_seed = 1.3

if (sys.argv[1] != "pwu" and sys.argv[1] != "auto"):
        companyNameSign = sys.argv[1]
        print "RM the old data file first\n"
        os.system("rm -rf %s-*"%(companyNameSign))
        run_strategy(investLen, rsiLen, companyNameSign, amount, True)
elif (sys.argv[1] == "auto"):
        while True:
                cur_time = time.time()
                cur_hour = datetime.datetime.today().hour
                if(cur_hour != 20 and initial_flag == True):
                        #print cur_time, "\n"
                        #print prv_time, "\n"
                        print cur_hour, "\n"
                        #print cur_time - prv_time, "\n"
                        #time.sleep(1800)
                else:
                        prv_time = cur_time

                        os.system("rm -rf database/*")
                        of = open(list_name, 'r')
                        lines = of.readlines()
                        for line in lines:
                                print '\n', line, '\n'

                                run_strategy(investLen, rsiLen, line.strip().lower(), amount, False)


                #analyze the result
                        # envaluate yesterday's result
                        pf_result_file = 'pf_result.txt'
			fpf = open(pf_result_file, 'w+')
                        fh = open('trading_result.txt', 'r+')
			lines = fh.readlines()
			for line in lines:
				print line
				if(re.match( r'^#', line, re.M|re.I) or re.match( r'^\s+', line, re.M|re.I)):
					pass
				else:
					ticker, yes_price, yes_average = line.split()
                                        print 'ticker = ', ticker, '\n'
                                        print 'yes_price = ', yes_price, '\n'
                                        print 'yes_average = ', yes_average, '\n'
                                	if(float(fund_stockquote.get_price(ticker)) > float(yes_price)):
						fpf.write('%s predict good :)\n'%(ticker))
					else:
						fpf.write('%s predict wrong :(\n'%(ticker))
			fh.close()
			fpf.close()
			
                        
                        #--------------------------------------------
                        sorted_trading_value = sorted(old_strategy.earning_stock.iteritems(), key=operator.itemgetter(1))
                        sorted_buying_value = sorted(old_strategy.buying_stock.iteritems(), key=operator.itemgetter(1))
                     	#print old_strategy.earning_stock
 			#print sorted_value
                        
                        ts = datetime.date.today()
			history_choice = 'trading_%s'%(ts)
                        os.system('cp %s history/%s'%(email_file, history_choice))
			
                        f1 = open('trading_result.txt', 'w+')
                        for entry in sorted_buying_value:
				if(fund_stockquote.eps_threshold(entry[0]) > 0 and (g_changing_range < (float(fund_stockquote.get_todays_high(entry[0])) - float(fund_stockquote.get_todays_low(entry[0])))/float(fund_stockquote.get_price(entry[0]))) and (float(fund_stockquote.get_volume(entry[0])) > 1.5*float(fund_stockquote.get_average_volume(entry[0])))):
					print entry[0]
                                	f1.write('%s %s %s'%(str(entry[0]), fund_stockquote.get_price(entry[0]), str(entry[-1])))
                                	f1.write('\n')
			f1.write("# Average curve up and results\n")
			#f1.write('\n')
			for entry in sorted_trading_value:
				 if(fund_stockquote.eps_threshold(entry[0]) > 0 and (float(fund_stockquote.get_volume(entry[0])) > 1.5*float(fund_stockquote.get_average_volume(entry[0]))) and (g_changing_range < (float(fund_stockquote.get_todays_high(entry[0])) - float(fund_stockquote.get_todays_low(entry[0])))/float(fund_stockquote.get_price(entry[0])))):
                                        print entry[0]
                                        f1.write('%s %s %s'%(str(entry[0]), fund_stockquote.get_price(entry[0]),str(entry[-1])))
                                        f1.write('\n')
                        f1.close()
                #print  earning_stock
                	initial_flag = True
			if(datetime.datetime.today().weekday() != 6):
				sendMail.sendToGmail(email_file)
				sendMail.sendToGmail(pf_result_file)
                time.sleep(1800)        
		
else:
        os.system("rm -rf database/*")
        of = open(list_name, 'r')
        lines = of.readlines()
        for line in lines:
                print '\n', line, '\n'

                run_strategy(investLen, rsiLen, line.strip().lower(), amount, False)


        #analyze the result
        sorted_value = sorted(earning_stock.iteritems(), key=operator.itemgetter(1))


        f1 = open('trading_result.txt', 'w+')
        for entry in sorted_value:
                f1.write(str(entry))
                f1.write('\n')


