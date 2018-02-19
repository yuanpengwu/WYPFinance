import fund_stockquote


ticker = "jst"
# test get_volume and get_average_volume

print "get_price = ", fund_stockquote.get_price(ticker)

print "get_volume = ", fund_stockquote.get_volume(ticker)

print "get_average_volume = ", fund_stockquote.get_average_volume(ticker)

print "get_todays_high = ",  fund_stockquote.get_todays_high(ticker)

print "get_todays_low = ", fund_stockquote.get_todays_low(ticker)
