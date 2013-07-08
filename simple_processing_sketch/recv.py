#!/usr/bin/python
import sys
import xmpp
import os
import signal
import time

def messageCB(conn,msg):
        print "Sender: " + str(msg.getFrom())
        print "Content: " + str(msg.getBody())
        #print msg
        content=str(msg.getBody())


def StepOn(conn):
        try:
                conn.Process(1)
        except KeyboardInterrupt:
                return 0
        return 1

def GoOn(conn):
        while StepOn(conn):
                pass

def main():

        jid="remotedev@wtfismyip.com/notify"
        pwd="remotedev"

        jid=xmpp.protocol.JID(jid)

        cl = xmpp.Client(jid.getDomain(), debug=[])

        if cl.connect() == "":
                print "not connected"
                sys.exit(0)

        if cl.auth(jid.getNode(),pwd) == None:
                print "authentication failed"
                sys.exit(0)

        cl.RegisterHandler('message', messageCB)

        cl.sendInitPresence()

        GoOn(cl)

main()