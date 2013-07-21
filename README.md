Glassware Physical Interaction Project
========================

Use Google glass voice command to control a LED on Arduino via XMPP messages.

You need a Arduino Ethernet or Arduino Ethernet Shield to try it in physical world.

Or you can run a XMPP client on your computer to try it.

Try it: [bareboneglass.appspot.com](http://bareboneglass.appspot.com)

First you need to use the button on left side to push a timeline card to your Google glass, and you can reply that card to send message to this app.

If you don't have an Arduino Ethernet off your hand. 
You can log a XMPP account on your computer and submit your XMPP account on bareboneglass.appspot.com.
Once you do that, all messages from your Glass will be forwared to your XMPP account. 
If you use your XMPP client to send **/push** *your message* to bareboneglass@appspot.com, the message will be forwarded to your Glass.

If you do have an Arduino Ethernet. You can use the Arduino sketch in this repository. 
After you change the XMPP account to your own account and upload the sketch, you can say "on" of "off" to toggle the led on pin9.
