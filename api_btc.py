#!/usr/bin/env python

import urllib2
import json

TICKER = "https://mtgox.com/code/data/ticker.php"
UNPAID_ELIGIUS_ST_US = "http://eligius.st/~artefact2/json/balance_unpaid_us_%s.json"
PAID_ELIGIUS_ST_US = "http://eligius.st/~artefact2/json/already_paid_us_%s.json"

def getticker():
    f = urllib2.urlopen(TICKER)
    resp = json.load(f)
    f.close()
    return resp

def getbalance_unpaid(address):
    f = urllib2.urlopen(UNPAID_ELIGIUS_ST_US % address)
    resp = json.load(f)
    f.close()
    return resp

def getbalance_paid(address):
    f = urllib2.urlopen(PAID_ELIGIUS_ST_US % address)
    resp = json.load(f)
    f.close()
    return resp

def test_ticker():
    ticker = getticker()
    print repr(ticker)
    print "Sell: {ticker[sell]}  Buy: {ticker[buy]}  High: {ticker[high]}  Low: {ticker[low]}  Last: {ticker[last]}  Vol: {ticker[vol]}".format(**ticker)

if __name__ == "__main__":
    try:
        ADDRESS = '1DFLXKsPTk4MRmVaAowraL9xFGewyUZGonx'
        unpaid = getbalance_unpaid(ADDRESS)
        print repr(unpaid[-1][1])
        paid = getbalance_paid(ADDRESS)
        print repr(paid[-1][1])
    except urllib2.HTTPError, e:
        print repr(e), str(e)
