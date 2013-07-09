#include <SPI.h>
#include <Base64.h>
#include <Ethernet.h>
#include <EthernetClient.h>

#include <XMPPClient.h>

byte mac[] = { 
  0x00, 0x11, 0x22, 0x33, 0x44, 0x55 };
char server[] = "wtfismyip.com";
char username[] = "remotedev";  //please change to your own account 
char password[] = "remotedev";
char resource[] = "test";

XMPPClient client;

int led = 9;

void setup()
{
  Serial.begin(9600);
  pinMode(led, OUTPUT);  
  client.xmppLogin(server, username, password, resource, mac);
  client.sendPresence();
  //client.sendMessage("bareboneglass@appspot.com","hello");
}


void loop() {
  char *message=client.receiveMessage();
  if (message!=NULL && strlen(message)>0){
    Serial.println(message);
    if (strstr(message,"on")!=NULL) digitalWrite(led, HIGH);
    if (strstr(message,"off")!=NULL) digitalWrite(led, LOW);
  }
}


