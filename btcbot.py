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
NICK="btc-bot"
IDENT="btc-bot"
REALNAME="Bitcoin Bot"
readbuffer=""
connected = True

s=socket.socket( )
s.connect((HOST, PORT))
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
            elif(line[1]=='PRIVMSG' and line[2] == NICK):
                cmd("JOIN", "#bhngaming")
            elif(line[1]=='PRIVMSG' and line[2].lower() == '#bhngaming'):
                try:
                    print len(line), repr(line)
                    if(line[3].lower()==":.btc" or line[3].lower()==":!btc"):
                        if(len(line) == 5 and line[4].lower()=="ticker"):
                            #{u'ticker': {u'sell': 19.25, u'buy': 19.030000000000001, u'last': 19.248999999999999, u'vol': 28982, u'high': 19.25, u'low': 18.25}}
                            ticker = api_btc.getticker()
                            ticker = "Sell: {ticker[sell]}  Buy: {ticker[buy]}  High: {ticker[high]}  Low: {ticker[low]}  Last: {ticker[last]}  Vol: {ticker[vol]}".format(**ticker)
                            cmd("PRIVMSG", "#bhngaming", ":"+ticker)
                        elif(len(line) == 6 and line[4].lower()=="tobtc"):
                            cmd_input = line[5].replace(USD, '').replace(',', '')
                            usd_value = float(cmd_input)
                            ticker = api_btc.getticker()['ticker']
                            inusd = usd_value / ticker['last']
                            resp = "{USD}{input} to BTC: {BTC}{value}".format(USD=USD, BTC=BTC, input=usd_value, value=inusd)
                            cmd("PRIVMSG", "#bhngaming", ":"+resp)
                        elif(len(line) == 6 and line[4].lower()=="tousd"):
                            cmd_input = line[5].replace(BTC, '').replace(',', '')
                            btc_value = float(cmd_input)
                            ticker = api_btc.getticker()['ticker']
                            inusd = btc_value * ticker['last']
                            resp = "{BTC}{input} to USD: {USD}{value}".format(USD=USD, BTC=BTC, input=btc_value, value=inusd)
                            cmd("PRIVMSG", "#bhngaming", ":"+resp)
                        elif(len(line) == 6 and line[4].lower()=="address"):
                            ADDRESS = line[5]
                            unpaid = api_btc.getbalance_unpaid(ADDRESS)[-1][1]
                            paid = api_btc.getbalance_paid(ADDRESS)[-1][1]
                            cmd("PRIVMSG", "#bhngaming", ":Address: {address}  Paid: {BTC}{paid}  Unpaid: {BTC}{unpaid}  Total: {BTC}{total}".format(BTC=BTC, address=ADDRESS, paid=paid, unpaid=unpaid, total=(paid+unpaid)))
                        elif(len(line) == 6 and line[4].lower()=="paid"):
                            ADDRESS = line[5]
                            paid = api_btc.getbalance_paid(ADDRESS)[-1][1]
                            cmd("PRIVMSG", "#bhngaming", ":Address: {address}  Paid: {BTC}{paid}".format(BTC=BTC, address=ADDRESS, paid=paid))
                        elif(len(line) == 6 and line[4].lower()=="unpaid"):
                            ADDRESS = line[5]
                            unpaid = api_btc.getbalance_unpaid(ADDRESS)[-1][1]
                            cmd("PRIVMSG", "#bhngaming", ":Address: {address}  Unpaid: {BTC}{unpaid}".format(BTC=BTC, address=ADDRESS, unpaid=unpaid))
                        else:
                            cmd("PRIVMSG", "#bhngaming", ":Available commands: TICKER TOBTC TOUSD ADDRESS PAID UNPAID")
                except ValueError, e:
                    cmd("PRIVMSG", "#bhngaming", ":Error: %s" % str(e))
                    traceback.print_exc(file=sys.stderr)
                except urllib2.HTTPError, e:
                    cmd("PRIVMSG", "#bhngaming", ":Error: %s" % str(e))
                    traceback.print_exc(file=sys.stderr)
            else:
                print repr(line)
    except KeyboardInterrupt:
        cmd("QUIT")
        connected = False
        s.close()
