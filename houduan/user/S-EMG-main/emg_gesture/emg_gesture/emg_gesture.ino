#include <EMGFilters.h>

#include <SoftwareSerial.h>

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif
#include "EMGFilters.h"
#define  SensorInputPin0 A0       //sensor input pin number

unsigned long threshold = 0;      // threshold: Relaxed baseline values.(threshold=0:in the calibration process)
unsigned long EMG_num = 0;      // EMG_num: The number of statistical signals
EMGFilters myFilter;
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;
SoftwareSerial BT(10, 11); //HC-06的RX和TX分别接D11和D10
void setup() 
{
  myFilter.init(sampleRate, humFreq, true, true, true);
  Serial.begin(115200);
  BT.begin(9600);  // 设置蓝牙串口波特率为9600
}
void loop() 
{
  int data0 = analogRead(SensorInputPin0);


  int dataAfterFilter0 = myFilter.update(data0);  

 
  Serial.print(dataAfterFilter0);
  Serial.print(",");    



  if (Serial.available())
  {
    char userInput = Serial.read();
    BT.println(userInput); // 将用户输入的数据通过蓝牙传输出去
  }

 

}
