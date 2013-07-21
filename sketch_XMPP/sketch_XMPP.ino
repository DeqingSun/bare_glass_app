#include <SPI.h>
#include <Base64.h>
#include <Ethernet.h>
#include <EthernetClient.h>

#include <XMPPClient.h>

#include <OneWire.h>

#define INTERVAL (15000)
#define PING_TIME_OUT (2000)
unsigned char time_out_counter=0;

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

unsigned long previousMillis = 0;
boolean pong_waiting=false;

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
  previousMillis = millis()-INTERVAL+2000;
}


void loop() {
  unsigned char got_message=false;
  char *message=client.receiveMessage(&got_message);

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

  unsigned long currentMillis = millis();

  if (pong_waiting){
    if (got_message) {//any response is valid
      pong_waiting=false; 
      time_out_counter=0;
      Serial.println(F("Got resp")); 
    }
    else if (currentMillis - previousMillis > PING_TIME_OUT){
      Serial.println(F("Time out")); 
      time_out_counter++;
      if (time_out_counter==2){
        Serial.println(F("Too many consecutive timeout")); 
        Serial.flush();
        asm volatile ("jmp 0");  //reset
      }
      pong_waiting=false; 
    }
  }

  if(currentMillis - previousMillis > INTERVAL) {
    previousMillis = currentMillis; 
    Serial.println(F("PING")); 
    client.sendPing(); 
    pong_waiting=true;
  }
}

















