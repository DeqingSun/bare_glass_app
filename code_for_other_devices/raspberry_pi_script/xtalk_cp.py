#!/usr/bin/python
# $Id: xtalk.py,v 1.4 2008/08/09 17:00:18 normanr Exp $
import sys,os,xmpp,time,select

import subprocess

from subprocess import call
import requests

class Bot:

    def __init__(self,jabber,remotejid):
        self.jabber = jabber
        self.remotejid = remotejid

    def register_handlers(self):
        self.jabber.RegisterHandler('message',self.xmpp_message)

    def xmpp_message(self, con, event):
        type = event.getType()
        fromjid = event.getFrom().getStripped()
        body = event.getBody()
        if type in ['message', 'chat', None] and fromjid == self.remotejid and body:
            sys.stdout.write(body + '\n')
            self.message_analyzer(body)


    def stdio_message(self, message):
        m = xmpp.protocol.Message(to=self.remotejid,body=message,typ='chat')
        self.jabber.send(m)

    def xmpp_connect(self):
        con=self.jabber.connect()
        if not con:
            sys.stderr.write('could not connect!\n')
            return False
        sys.stderr.write('connected with %s\n'%con)
        auth=self.jabber.auth(jid.getNode(),password,resource=jid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!\n')
            return False
        sys.stderr.write('authenticated using %s\n'%auth)
        self.register_handlers()
        return con
    
    def message_analyzer(self,body):	#handle incoming messages
        if (body.find('temperature')>=0):
            sys.stdout.write('sample internal temperature' + '\n')
            temperature_result=subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"]).strip()
            self.stdio_message("/push CPU temperature of Pi is: "+temperature_result[5:])
        if (body.find('picture')>=0):
            call("fswebcam -S 20 -q --no-banner --crop 640x360 -r 640x480 -d /dev/video0 pic.jpg", shell=True)
            if os.path.exists("pic.jpg"):
                payload = {'xmpp_addr': 'remotedev@wtfismyip.com/pi', 'msg': 'Photo from Pi'}
                my_files = {'file': open('pic.jpg', 'rb')}
                r = requests.post('https://bareboneglass.appspot.com/upload',data=payload,files=my_files)
                sys.stdout.write(str(r.status_code)+'\n')
                sys.stdout.write(r.text)
                os.remove("pic.jpg")
            else:
                sys.stdout.write("Something wrong with camera")  

    
if __name__ == '__main__':

    #if len(sys.argv) < 2:
    #    print "Syntax: xtalk JID"
    #    sys.exit(0)
    
    #tojid=sys.argv[1]
    tojid='bareboneglass@appspot.com'
    
    source = 'remotedev@wtfismyip.com/pi'	#change it to your own
    password = 'remotedev'					#change it to your own
    target = 'bareboneglass@appspot.com'
    
    jid=xmpp.protocol.JID(source)
    cl=xmpp.Client(jid.getDomain())#,debug=[])
    
    bot=Bot(cl,tojid)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)

    #cl.SendInitPresence(requestRoster=0)   # you may need to uncomment this for old server
    
    socketlist = {cl.Connection._sock:'xmpp',sys.stdin:'stdio'}
    online = 1

    while online:
        (i , o, e) = select.select(socketlist.keys(),[],[],1)
        for each in i:
            if socketlist[each] == 'xmpp':
                cl.Process(1)
            elif socketlist[each] == 'stdio':
                msg = sys.stdin.readline().rstrip('\r\n')
                bot.stdio_message(msg)
            else:
                raise Exception("Unknown socket type: %s" % repr(socketlist[each]))
    #cl.disconnect()
