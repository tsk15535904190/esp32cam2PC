#include <WiFi.h>
#include <AsyncUDP.h>
#include "camera_pins.h"
#include "esp_camera.h"

const char* ssid = "shumei521";
const char* password = "tsk980820";
AsyncUDP udp;
camera_fb_t *fb = NULL;

void setup() {
  Serial.begin(115200);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

    if(config.pixel_format == PIXFORMAT_JPEG){
    if(psramFound()){
      config.jpeg_quality = 1;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
      Serial.println("psramFound!");
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_VGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_VGA;
  }

    esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  
  sensor_t * s = esp_camera_sensor_get();
    if(config.pixel_format == PIXFORMAT_JPEG){
    s->set_framesize(s, FRAMESIZE_VGA);
  }

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

      if(udp.connect(IPAddress(124,223,103,23), 8080)) {
        Serial.println("UDP connected");
        udp.onPacket([](AsyncUDPPacket packet) {
            Serial.print(", Data: ");
            Serial.write(packet.data(), packet.length());
            Serial.println();
            //reply to the client
            //packet.printf("Got %u bytes of data", packet.length());
        });
        //Send unicast
        udp.print("ESP32");//上电后发送ESP32代表摄像机上线
    }

    pinMode(4, OUTPUT);    //开始闪闪灯
    digitalWrite(4, HIGH); // 
    delay(200);
    digitalWrite(4, LOW);
}
#define max_packet_byte 1400  //UDP传输大小有限制，因此一个包最大1400+1位引导位
uint8_t onePacket[max_packet_byte+1];
/*
*分发包思想
*一张图片大概是3K~10K之间
*每个包数据大小为1400，增加一位索引位，告诉服务器我是第几个包
*索引位为0xff时代表是最后一个包，便于上位机处理
*/
void sendImgAray(uint8_t * img,uint16_t lenth,uint8_t index)
{
  memset(onePacket,0x00,max_packet_byte+1);
  memcpy(onePacket,fb->buf,lenth);
  onePacket[lenth]=index;
  udp.write(onePacket, lenth+1);
}
void loop() {
  if(!udp.connected())
  {
    udp.connect(IPAddress(192,168,2,210), 8080);
    Serial.println("is not connected!");
    delay(1000);  
  }
  else
  {
    delay(20);
    fb = esp_camera_fb_get();
    if(!fb)
    {
        Serial.println("read fail!");
    }
    else
    {
        Serial.print("get a img size:");
        Serial.println(fb->len);
  
        uint8_t *P_temp = fb->buf;                            //暂存指针初始位置
        int pic_length = fb->len;                             //获取图片字节数量
        int pic_pack_quantity = pic_length / max_packet_byte; //将图片分包时可以分几个整包
        int remine_byte = pic_length % max_packet_byte;       //余值,即最后一个包的大小
        
        for (int j = 0; j < pic_pack_quantity; j++) //发送图片信息,这是按分包循环发送,每一次循环发送一个包,包的大小就是上面指定的1024个字节.
        {
            sendImgAray(fb->buf, max_packet_byte,j); //将图片分包发送
            fb->buf+=max_packet_byte; //图片内存指针移动到相应位置
        }
        sendImgAray(fb->buf, remine_byte,0xFF); //发送最后一个包，剩余的数据
        fb->buf = P_temp;         //将当时保存的指针重新返还最初位置
        esp_camera_fb_return(fb);
    }
  }
}
