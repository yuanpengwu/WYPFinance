import itertools
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.optimizer import server
import sys, os
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.tools import yahoofinance

def parameters_generator():
    entrySMA = range(251, 281)
    exitSMA = range(11, 21)
    rsiPeriod = range(10, 14)
    overBoughtThreshold = range(75, 90)
    overSoldThreshold = range(5, 21)
    return itertools.product(entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)

# The if __name__ == '__main__' part is necessary if running on Windows.
if __name__ == '__main__':
    # Load the feed from the CSV files.
    #feed = yahoofeed.Feed()
    instrument = sys.argv[1]
    os.system("rm -rf %s-*"%(instrument))
    feed = yahoofinance.build_feed([instrument], 2011, 2014, "./database")
    #feed.addBarsFromCSV(instrument, "%s-2011-yahoofinance.csv"%(instrument))
    #feed.addBarsFromCSV(instrument, "%s-2012-yahoofinance.csv"%(instrument))
    #feed.addBarsFromCSV(instrument, "%s-2013-yahoofinance.csv"%(instrument))
    #feed.addBarsFromCSV(instrument, "%s-2014-yahoofinance.csv"%(instrument))
    # Run the server.
    server.serve(feed, parameters_generator(), "localhost", 5000)
