#include <SPI.h>
#include <Base64.h>
#include <Ethernet.h>
#include <EthernetClient.h>

#include <XMPPClient.h>

#include <OneWire.h>



byte mac[] = { 
  0x00, 0x11, 0x22, 0x33, 0x44, 0x55 };
char server[] = "wtfismyip.com";
char username[] = "remotedev";  //please change to your own account 
char password[] = "remotedev";
char resource[] = "test";

XMPPClient client;

int led = 9;

byte addr[8];
char buffer [50];

OneWire  ds(A2);  

void setup()
{
  Serial.begin(9600);
  pinMode(led, OUTPUT);  
  Serial.println(F("Initialization..."));
  while(client.xmppLogin(server, username, password, resource, mac)<=0){
    delay(1000);
    Serial.println(F("TRY RECONNECT"));
  }
  client.sendPresence();

  pinMode(A1,OUTPUT);
  pinMode(A3,OUTPUT);
  digitalWrite(A1,LOW);
  digitalWrite(A3,HIGH);
  init_18b20();
}


void loop() {
  char *message=client.receiveMessage();
  if (message!=NULL && strlen(message)>0){
    Serial.println(message);
    if (strstr(message,"on")!=NULL) digitalWrite(led, HIGH);
    if (strstr(message,"off")!=NULL) digitalWrite(led, LOW);
    if (strstr(message,"temperature")!=NULL) {
      unsigned int a=get_temperature();
      unsigned char i_p=a/16;
      unsigned char f_p=(a%16)*6+(a%16)/4;
      sprintf (buffer, "/push Temperature is: %d.%02dC", i_p,f_p);
      client.sendMessage("bareboneglass@appspot.com",buffer);
    }
  }
}







