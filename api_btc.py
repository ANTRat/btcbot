#!/usr/bin/env python

import urllib2
import json
import locale
import re

TICKER = "https://mtgox.com/code/data/ticker.php"
UNPAID_ELIGIUS_ST = "http://eligius.st/~artefact2/json/balance_unpaid_%s_%s.json"
PAID_ELIGIUS_ST = "http://eligius.st/~artefact2/json/already_paid_%s_%s.json"
CURRENTBLOCK_ELIGIUS_ST = "http://eligius.st/~artefact2/json/balance_current_block_%s_%s.json"

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

LOCALE = locale.getlocale()
BTC='\xe0\xb8\xbf'
LOCALE_CRNCYSTR=locale.nl_langinfo(locale.CRNCYSTR)

def getcurrencyre(CURRENCY):
    """Return a re object suitable to parse locale.CRNCYSTR"""
    CURRENCY_SYM = re.escape(CURRENCY[1:])
    if(CURRENCY[0]=='-'):
        CURRENCY_RE = re.compile("^%s" % CURRENCY_SYM)
    elif(CURRENCY[0]=='+'):
        CURRENCY_RE = re.compile("%s$" % CURRENCY_SYM)
    else:
        raise ValueError("locales that replace the radix character with the currency symbol are not supported at this time")
    
    return CURRENCY_RE

LOCALE_CRNCY_RE = getcurrencyre(LOCALE_CRNCYSTR)
BTC_CRNCY_RE = getcurrencyre('-' + BTC)
BTC2_CRNCY_RE = getcurrencyre('-B')

def getticker():
    f = urllib2.urlopen(TICKER)
    resp = json.load(f)
    f.close()
    return resp

def getbalance_unpaid(address, pool=None):
    if pool == None:
        return getbalance_unpaid(address, 'eu') + getbalance_unpaid(address, 'us')
    else:
        f = urllib2.urlopen(UNPAID_ELIGIUS_ST % (pool, address))
        resp = json.load(f)[-1][1]
        f.close()
        return resp


def getbalance_paid(address, pool=None):
    if pool == None:
        return getbalance_paid(address, 'eu') + getbalance_paid(address, 'us')
    else:
        f = urllib2.urlopen(PAID_ELIGIUS_ST % (pool, address))
        resp = json.load(f)[-1][1]
        f.close()
        return resp

def getbalance_currentblock(address, pool=None):
    if pool == None:
        return getbalance_currentblock(address, 'eu') + getbalance_currentblock(address, 'us')
    else:
        f = urllib2.urlopen(CURRENTBLOCK_ELIGIUS_ST % (pool, address))
        resp = json.load(f)[-1][1]
        f.close()
        return resp

def cur_to_locale(value, international=False):
    return locale.currency(value, True, True, international=international)

def cur_to_btc(value):
    value = locale.format("%.8f", value, grouping=True)
    return "".join([BTC, value])

def cur_parse(value):
    """
    Parses input into a float value
    Returns a tuple of (CURRENCY, value)
    CURRENCY is the locale that was parsed, or 'BTC'
    value is the ammount devoid of grouping and currency strings in a float
    """
    locale_value, repl_count = LOCALE_CRNCY_RE.subn('', value)
    if(repl_count >= 1):
        # we matched the current locale
        locale_value = locale.atof(locale_value)
        return (LOCALE[0], locale_value)
    btc_value, repl_count = BTC_CRNCY_RE.subn('', value)
    if(repl_count >= 1):
        # we matched BTC
        btc_value = locale.atof(btc_value)
        return ('BTC', btc_value)

    btc_value, repl_count = BTC2_CRNCY_RE.subn('', value)
    if(repl_count >= 1):
        # we matched BTC2
        btc_value = locale.atof(btc_value)
        return ('BTC', btc_value)

    raise ValueError("Unknown locale for currency: %s" % value)

# >>> locale.currency(1234567890.0987654321, True, True)
# '$1,234,567,890.10'
# >>> locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def test_ticker():
    ticker = getticker()
    print repr(ticker)
    print "Sell: {ticker[sell]}  Buy: {ticker[buy]}  High: {ticker[high]}  Low: {ticker[low]}  Last: {ticker[last]}  Vol: {ticker[vol]}".format(**ticker)

if __name__ == "__main__":
    value = BTC+"1,234,567,890"
    print cur_parse(value)
    value = "$1,234,567,890"
    print cur_parse(value)
    try:
        ADDRESS = '1DFLXKsPTk4MRmVaAowraL9xFGewyUZGon'
        unpaid_both = getbalance_unpaid(ADDRESS)
        print unpaid_both
        assert unpaid_both == getbalance_unpaid(ADDRESS,'us')  + getbalance_unpaid(ADDRESS,'eu')
        paid_both = getbalance_paid(ADDRESS)
        print paid_both
        assert paid_both == getbalance_paid(ADDRESS,'us')  + getbalance_paid(ADDRESS,'eu')
    except urllib2.HTTPError, e:
        print repr(e), str(e)
