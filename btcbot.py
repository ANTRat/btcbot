#!/usr/bin/env python

import sys
import socket
import string
import api_btc
import urllib2
import sys
import traceback

USD="$"
BTC='\xe0\xb8\xbf'
HOST="irc.gamesurge.net"
PORT=6667
PASS=None
NICK="btc-bot"
IDENT="btc-bot"
REALNAME="Bitcoin Bot"
CHAN='#bhngaming'
readbuffer=""
connected = True

s=socket.socket( )
s.connect((HOST, PORT))
if PASS:
    s.send("PASS %s\r\n" % PASS)
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))

def cmd(*args):
    command = " ".join(args)
    print "sending:", command
    s.send("%s\r\n" % command)

while connected:
    try:
        readbuffer=readbuffer+s.recv(1024)
        temp=string.split(readbuffer, "\n")
        readbuffer=temp.pop( )

        for line in temp:
            line=string.rstrip(line)
            line=string.split(line)

            if(line[0]=="PING"):
                s.send("PONG %s\r\n" % line[1])
            elif(line[1]=="NOTICE"):
                pass
            elif(line[1]=='433' and line[3] == NICK):
                 NICK+='`'
                 cmd("NICK", NICK)
            elif(line[1]=='001' and line[2] == NICK):
                cmd("JOIN", CHAN)
            elif(line[1]=='PRIVMSG' and line[2].lower() == CHAN):
                try:
                    print len(line), repr(line)
                    if(line[3].lower()==":.btc" or line[3].lower()==":!btc"):
                        if(len(line) == 5 and line[4].lower()=="ticker"):
                            #{u'ticker': {u'sell': 19.25, u'buy': 19.030000000000001, u'last': 19.248999999999999, u'vol': 28982, u'high': 19.25, u'low': 18.25}}
                            ticker = api_btc.getticker()
                            ticker = "Sell: {ticker[sell]}  Buy: {ticker[buy]}  High: {ticker[high]}  Low: {ticker[low]}  Last: {ticker[last]}  Vol: {ticker[vol]}".format(**ticker)
                            cmd("PRIVMSG", CHAN, ":"+ticker)
                        elif(len(line) == 6 and line[4].lower()=="tobtc"):
                            cmd_input = line[5].replace(USD, '').replace(',', '')
                            usd_value = float(cmd_input)
                            ticker = api_btc.getticker()['ticker']
                            inusd = usd_value / ticker['last']
                            resp = "{USD}{input} to BTC: {BTC}{value}".format(USD=USD, BTC=BTC, input=usd_value, value=inusd)
                            cmd("PRIVMSG", CHAN, ":"+resp)
                        elif(len(line) == 6 and line[4].lower()=="tousd"):
                            cmd_input = line[5].replace(BTC, '').replace(',', '')
                            btc_value = float(cmd_input)
                            ticker = api_btc.getticker()['ticker']
                            inusd = btc_value * ticker['last']
                            resp = "{BTC}{input} to USD: {USD}{value}".format(USD=USD, BTC=BTC, input=btc_value, value=inusd)
                            cmd("PRIVMSG", CHAN, ":"+resp)
                        elif((len(line) == 6 or len(line) == 7) and line[4].lower()=="address"):
                            ADDRESS = line[5]
                            POOL = None
                            if len(line) == 7:
                                POOL = line[6]
                            unpaid = api_btc.getbalance_unpaid(ADDRESS, POOL)
                            paid = api_btc.getbalance_paid(ADDRESS, POOL)
                            block = api_btc.getbalance_currentblock(ADDRESS, POOL)
                            cmd("PRIVMSG", CHAN, ":Address: {address}  Paid: {BTC}{paid}  Unpaid: {BTC}{unpaid}  CurrentBlock: {BTC}{block}  Total: {BTC}{total}".format(BTC=BTC, address=ADDRESS, paid=paid, unpaid=unpaid, block=block, total=(paid+unpaid+block)))
                        elif((len(line) == 6 or len(line) == 7) and line[4].lower()=="paid"):
                            ADDRESS = line[5]
                            POOL = None
                            if len(line) == 7:
                                POOL = line[6]
                            paid = api_btc.getbalance_paid(ADDRESS, POOL)
                            cmd("PRIVMSG", CHAN, ":Address: {address}  Paid: {BTC}{paid}".format(BTC=BTC, address=ADDRESS, paid=paid))
                        elif((len(line) == 6 or len(line) == 7) and line[4].lower()=="unpaid"):
                            ADDRESS = line[5]
                            POOL = None
                            if len(line) == 7:
                                POOL = line[6]
                            unpaid = api_btc.getbalance_unpaid(ADDRESS, POOL)
                            cmd("PRIVMSG", CHAN, ":Address: {address}  Unpaid: {BTC}{unpaid}".format(BTC=BTC, address=ADDRESS, unpaid=unpaid))
                        elif(len(line) == 6 and line[4].lower()=="convert"):
                            input_value = line[5]
                            input_locale, value = api_btc.cur_parse(input_value)
                            if(input_locale == 'en_US'):
                                ticker = api_btc.getticker()['ticker']
                                resp = api_btc.cur_to_btc(value / ticker['last'])
                            elif(input_locale == 'BTC'):
                                ticker = api_btc.getticker()['ticker']
                                resp = api_btc.cur_to_locale(value * ticker['last'])
                            else:
                                raise ValueError("Unknown input locale: %s" % input_locale)

                            cmd("PRIVMSG", CHAN, ":{input_value} is valued at {dest_value}".format(
                                input_value = input_value,
                                dest_value = resp
                            ))
                        else:
                            cmd("PRIVMSG", CHAN, ":Available commands: TICKER CONVERT ADDRESS TOBTC TOUSD PAID UNPAID")
                except ValueError, e:
                    cmd("PRIVMSG", CHAN, ":Error: %s" % str(e))
                    traceback.print_exc(file=sys.stderr)
                except urllib2.HTTPError, e:
                    cmd("PRIVMSG", CHAN, ":Error: %s" % str(e))
                    traceback.print_exc(file=sys.stderr)
            else:
                print repr(line)
    except KeyboardInterrupt:
        cmd("QUIT")
        connected = False
        s.close()
