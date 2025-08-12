#include <WiFi.h>
#include <WiFiUdp.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>  // 引入 I2C 库
#include <WiFiManager.h>  // 引入 Wi-Fi Manager 库

// // 设置 Wi-Fi 网络
// const char* ssid = "Magic5_Pro";  // 替换为你的 Wi-Fi 名称
// const char* password = "20050825";  // 替换为你的 Wi-Fi 密码
// const char* ssid = "iPhone Des";  // 设置Wi-Fi名称为 "iPhone Des"
// const char* password = "yanghe20050825";  // 设置Wi-Fi密码为 "yanghe20050825"

// 设置目标 IP 地址和端口（更改为 UDP 的端口）
const char* serverIP = "115.190.118.22";  // 目标服务器的 IP 地址
const int serverPort = 6000;  // 更改为新的 UDP 端口号
WiFiUDP udp;  // 创建 UDP 对象a

int sendCount = 0;  // 全局计数器，记录发送次数

// 创建 UART2 用于接收数据
HardwareSerial mySerial2(2);  // 使用 UART2

// 设置用于存储解析后的数值
float values[10][3];  // 存储 10 条数据，每条数据 3 个浮动数值
int dataCount = 0;  // 当前缓冲区内的接收数据条数

// OLED 屏幕设置
#define SCREEN_WIDTH 128  // OLED 宽度
#define SCREEN_HEIGHT 32  // OLED 高度
#define OLED_RESET    -1  // OLED 重置引脚
#define SCREEN_ADDRESS 0x3C  // SSD1306 I2C 地址，常见为 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);  // 创建 OLED 对象

// 创建一个数组存储显示的波形数据点
int waveform[SCREEN_WIDTH];  // 存储 128 个像素点的波形数据

void parseData(String data, int index) {
  int index1 = data.indexOf(',');  // 找到第一个逗号
  int index2 = data.indexOf(',', index1 + 1);  // 找到第二个逗号

  if (index1 != -1 && index2 != -1) {
    // 提取每个数值，并转换为浮动数值
    values[index][0] = data.substring(0, index1).toFloat();  // 从开头到第一个逗号
    values[index][1] = data.substring(index1 + 1, index2).toFloat();  // 从第一个到第二个逗号
    values[index][2] = data.substring(index2 + 1).toFloat();  // 从第二个逗号到结尾
  }
}

// 通过 UDP 向服务器发送数据
void sendToComputer() {
  if (WiFi.status() == WL_CONNECTED) {
    // 格式化数据为 JSON 格式
    String jsonData = "[";  // 开始 JSON 数组
    for (int i = 0; i < 10; i++) {
      jsonData += "[" + String(values[i][0]) + "," + String(values[i][1]) + "," + String(values[i][2]) + "]";
      if (i < 9) {
        jsonData += ",";  // 连接数组项
      }
    }
    jsonData += "]";  // 结束 JSON 数组

    // 发送数据到目标服务器的 UDP 地址和端口
    udp.beginPacket(serverIP, serverPort);
    udp.print(jsonData);  // 发送 JSON 数据
    udp.endPacket();  // 结束数据包发送

    // sendCount++;  // 增加计数器

    // Serial.println("Data sent via UDP: ");
    // Serial.println(jsonData);  // 打印发送的 JSON 数据
    // Serial.print("Total messages sent: ");
    Serial.println(sendCount);  // 打印发送的次数
  } else {
    Serial.println("Error in WiFi connection");
  }
}

// OLED 初始化函数
void setupOLED() {
  // 设置 I2C 引脚：SDA = GPIO21，SCL = GPIO47
  Wire.begin(21, 47);  // 显式设置 I2C 的 SDA 和 SCL 引脚

  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) { // 正确的参数顺序
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // 如果初始化失败，停止程序
  }
  display.display();  // 显示初始化画面
  delay(2000);  // 等待 2 秒
  display.clearDisplay();  // 清空显示内容
}

// 绘制持续的波形图，填充到 OLED 屏幕的 128 个像素点
void drawWaveform(float data[10][3]) {
  // 将数据值映射到 OLED 屏幕的高度范围
  int xPos = SCREEN_WIDTH - 1;  // 起始绘制位置在屏幕右边

  // 将每个通道的信号绘制为波形
  for (int i = 0; i < SCREEN_WIDTH - 1; i++) {
    waveform[i] = waveform[i + 1];  // 向左滚动数据点
  }

  // 获取最新的信号并进行归一化映射
  int rawValue = values[dataCount % 10][0];  // 使用第一个信号值
  int normalizedValue = map(rawValue, -400, 400, 0, SCREEN_HEIGHT);  // 假设信号值的范围是 -400 到 400，进行映射

  // 将最新的值放入波形数组的末尾
  waveform[SCREEN_WIDTH - 1] = normalizedValue;

  // 清除屏幕并重新绘制波形
  display.clearDisplay();
  for (int i = 1; i < SCREEN_WIDTH; i++) {
    display.drawLine(i - 1, SCREEN_HEIGHT - waveform[i - 1], i, SCREEN_HEIGHT - waveform[i], SSD1306_WHITE);  // 连接每个点形成曲线
  }
  display.display();  // 更新 OLED 屏幕显示
}

void setup() {
  Serial.begin(115200);
  // 打印上次复位原因
  esp_reset_reason_t reason = esp_reset_reason();
  WiFiManager wifiManager;

  // 连接 Wi-Fi
  // 启动并等待连接 Wi-Fi 网络，Web 配网界面会自动出现
  if (!wifiManager.autoConnect("ESP32-Access-Point")) {  // ESP32 设置为热点模式
    Serial.println("Failed to connect and hit timeout");
    // 进入失败处理
    ESP.restart();  // 重启 ESP32，重新启动配网过程
  }
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());  // 打印 ESP32 的 IP 地址

  // 初始化 UART2
  mySerial2.begin(9600, SERIAL_8N1, 16, 17);  // UART2，TX = 17，RX = 16

  // 初始化 OLED 屏幕
  setupOLED();
}

void loop() {
  // 检查是否从串口接收到数据
  if (mySerial2.available() > 0) {
    // 从串口读取数据直到换行符
    String incomingData = mySerial2.readStringUntil('\n');
    Serial.print("Received from UART2: ");
    Serial.println(incomingData);  // 打印接收到的数据

    // 将数据存储到缓冲区
    if (dataCount < 10) {
      parseData(incomingData, dataCount);  // 将数据解析并存储
      dataCount++;
    }

    // 每 10 条数据后发送一次
    if (dataCount >= 10) {
      // 发送数据到服务器
      sendToComputer();

      // 在 OLED 屏幕上显示波形图
      drawWaveform(values);
      
      // 清空缓冲区并准备接收下一批数据
      dataCount = 0;
    }
  }

  delay(0.1);  // 控制读取频率，避免读取过快
}
// #include <WiFi.h>
// #include <WiFiUdp.h>
// #include <Adafruit_GFX.h>
// #include <Adafruit_SSD1306.h>
// #include <Wire.h>  // 引入 I2C 库

// // // 设置 Wi-Fi 网络
// // const char* ssid = "TP-LINK_B488";  // 替换为你的 Wi-Fi 名称
// // const char* password = "UXVH5T7E";  // 替换为你的 Wi-Fi 密码
// const char* ssid = "iPhone Des";  // 设置Wi-Fi名称为 "iPhone Des"
// const char* password = "yanghe20050825";  // 设置Wi-Fi密码为 "yanghe20050825"

// // 设置目标 IP 地址和端口（更改为 UDP 的端口）
// const char* serverIP = "115.190.134.66";  // 目标服务器的 IP 地址
// const int serverPort = 6000;  // 更改为新的 UDP 端口号
// int sendCount = 0;  // 全局计数器，记录发送次数

// WiFiUDP udp;  // 创建 UDP 对象

// // 创建 UART2 用于接收数据
// HardwareSerial mySerial2(2);  // 使用 UART2

// // 设置用于存储解析后的数值
// float values[10][3];  // 存储 10 条数据，每条数据 3 个浮动数值
// int dataCount = 0;  // 当前缓冲区内的接收数据条数

// // OLED 屏幕设置
// #define SCREEN_WIDTH 128  // OLED 宽度
// #define SCREEN_HEIGHT 32  // OLED 高度
// #define OLED_RESET    -1  // OLED 重置引脚
// #define SCREEN_ADDRESS 0x3C  // SSD1306 I2C 地址，常见为 0x3C
// Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);  // 创建 OLED 对象

// // 创建一个数组存储显示的波形数据点
// int waveform[SCREEN_WIDTH];  // 存储 128 个像素点的波形数据

// void parseData(String data, int index) {
//   int index1 = data.indexOf(',');  // 找到第一个逗号
//   int index2 = data.indexOf(',', index1 + 1);  // 找到第二个逗号

//   if (index1 != -1 && index2 != -1) {
//     // 提取每个数值，并转换为浮动数值
//     values[index][0] = data.substring(0, index1).toFloat();  // 从开头到第一个逗号
//     values[index][1] = data.substring(index1 + 1, index2).toFloat();  // 从第一个到第二个逗号
//     values[index][2] = data.substring(index2 + 1).toFloat();  // 从第二个逗号到结尾
//   }
// }

// // 通过 UDP 向服务器发送数据
// void sendToComputer() {
//   if (WiFi.status() == WL_CONNECTED) {
//     // 格式化数据为 JSON 格式
//     String jsonData = "[";  // 开始 JSON 数组
//     for (int i = 0; i < 10; i++) {
//       jsonData += "[" + String(values[i][0]) + "," + String(values[i][1]) + "," + String(values[i][2]) + "]";
//       if (i < 9) {
//         jsonData += ",";  // 连接数组项
//       }
//     }
//     jsonData += "]";  // 结束 JSON 数组

//     // 发送数据到目标服务器的 UDP 地址和端口
//     udp.beginPacket(serverIP, serverPort);
//     udp.print(jsonData);  // 发送 JSON 数据
//     udp.endPacket();  // 结束数据包发送

//     // sendCount++;  // 增加计数器

//     // Serial.println("Data sent via UDP: ");
//     // Serial.println(jsonData);  // 打印发送的 JSON 数据
//     // Serial.print("Total messages sent: ");
//     Serial.println(sendCount);  // 打印发送的次数
//   } else {
//     Serial.println("Error in WiFi connection");
//   }
// }


// // OLED 初始化函数
// void setupOLED() {
//   // 设置 I2C 引脚：SDA = GPIO21，SCL = GPIO47
//   Wire.begin(21, 47);  // 显式设置 I2C 的 SDA 和 SCL 引脚

//   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) { // 正确的参数顺序
//     Serial.println(F("SSD1306 allocation failed"));
//     for(;;); // 如果初始化失败，停止程序
//   }
//   display.display();  // 显示初始化画面
//   delay(2000);  // 等待 2 秒
//   display.clearDisplay();  // 清空显示内容
// }

// // 绘制持续的波形图，填充到 OLED 屏幕的 128 个像素点
// void drawWaveform(float data[10][3]) {
//   // 将数据值映射到 OLED 屏幕的高度范围
//   int xPos = SCREEN_WIDTH - 1;  // 起始绘制位置在屏幕右边

//   // 将每个通道的信号绘制为波形
//   for (int i = 0; i < SCREEN_WIDTH - 1; i++) {
//     waveform[i] = waveform[i + 1];  // 向左滚动数据点
//   }

//   // 获取最新的信号并进行归一化映射
//   int rawValue = values[dataCount % 10][0];  // 使用第一个信号值
//   int normalizedValue = map(rawValue, -400, 400, 0, SCREEN_HEIGHT);  // 假设信号值的范围是 -400 到 400，进行映射

//   // 将最新的值放入波形数组的末尾
//   waveform[SCREEN_WIDTH - 1] = normalizedValue;

//   // 清除屏幕并重新绘制波形
//   display.clearDisplay();
//   for (int i = 1; i < SCREEN_WIDTH; i++) {
//     display.drawLine(i - 1, SCREEN_HEIGHT - waveform[i - 1], i, SCREEN_HEIGHT - waveform[i], SSD1306_WHITE);  // 连接每个点形成曲线
//   }
//   display.display();  // 更新 OLED 屏幕显示
// }

// void setup() {
//   Serial.begin(115200);
//   // 打印上次复位原因
//   esp_reset_reason_t reason = esp_reset_reason();
//   Serial.print("Reset reason: ");
//   Serial.println(reason);

//   // 连接 Wi-Fi
//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.println("Connecting to WiFi...");
//   }
//   Serial.println("Connected to WiFi");

//   // 初始化 UART2
//   mySerial2.begin(9600, SERIAL_8N1, 16, 17);  // UART2，TX = 17，RX = 16

//   // 初始化 OLED 屏幕
//   setupOLED();
// }

// void loop() {
//   // 检查是否从串口接收到数据
//   if (mySerial2.available() > 0) {
//     // 从串口读取数据直到换行符
//     String incomingData = mySerial2.readStringUntil('\n');
//     Serial.print("Received from UART2: ");
//     Serial.println(incomingData);  // 打印接收到的数据

//     // 将数据存储到缓冲区
//     if (dataCount < 10) {
//       parseData(incomingData, dataCount);  // 将数据解析并存储
//       dataCount++;
//     }

//     // 每 10 条数据后发送一次
//     if (dataCount >= 10) {
//       // 发送数据到服务器
//       sendToComputer();

//       // 在 OLED 屏幕上显示波形图
//       drawWaveform(values);
      
//       // 清空缓冲区并准备接收下一批数据
//       dataCount = 0;
//     }
//   }

//   delay(0.1);  // 控制读取频率，避免读取过快
// }
