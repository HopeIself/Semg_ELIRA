#include <EMGFilters.h>

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#define SensorInputPin0 A0  // EMG 传感器连接的模拟输入引脚
unsigned long threshold = 0; 
unsigned long EMG_num = 0;  

EMGFilters myFilter;
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

void setup() {
  myFilter.init(sampleRate, humFreq, true, true, true);
  Serial.begin(115200);  // 向电脑发送数据的串口，波特率要和Python代码一致
}

void loop() {
  int data0 = analogRead(SensorInputPin0);           // 读取原始模拟值
  int dataAfterFilter0 = myFilter.update(data0);     // 经过滤波处理

  Serial.println(dataAfterFilter0);  // 只发送滤波后单个整数，并自动换行

  delay(2);  // 控制数据频率，500Hz = 2ms 一次
}
