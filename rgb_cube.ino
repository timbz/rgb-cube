#include <PacketSerial.h>
#include <Colorduino.h>

PacketSerial packetSerial;

void onPacketReceived(const uint8_t* buffer, size_t size){
  uint8_t x = 0;
  uint8_t y = 0;
  for (size_t i = 0; i < size; i+=3) {
    Colorduino.SetPixel(x, y, buffer[i], buffer[i+1], buffer[i+2]);
    x++;
    if (x >= ColorduinoScreenWidth) {
      x = 0;
      y++;
    }
    if (y >= ColorduinoScreenHeight) {
      break;
    }
  }
  Colorduino.FlipPage();
}

void setup()
{
  Colorduino.Init(); // initialize the board
  
  unsigned char whiteBalVal[3] = {36,63,63}; // for LEDSEE 6x6cm round matrix
  Colorduino.SetWhiteBal(whiteBalVal);
  
  Serial.begin(115200);  
  packetSerial.setStream(&Serial);
  packetSerial.setPacketHandler(&onPacketReceived);

  Colorduino.SetPixel(0, 0, 255, 255, 255); // enable 1 led to test functionality
  Colorduino.FlipPage();
}

void loop()
{
  packetSerial.update();
}
