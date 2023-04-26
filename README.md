# esp32cam2PC
硬件：ESP32-CAM
ESP32开发环境：Arduino

python依赖库：opencv-python

你可以选择在公网服务器或者内网电脑接受来自于ESP32的图像，使用python运行esp32ImgOnServer.py，其中python脚本中的IP地址为电脑本地IP地址，ESP32代码中广播的IP地址
要修改为接受图像的电脑的IP地址

可以配置是否保存图像

你如果在服务器接受图像，可以通过esp32ImgOnLocalPc.py接受从服务器转发过来的图像，脚本中的IP地址为服务器的IP

已知问题，中国移动宽带在多次开启关闭转发后转发率会逐渐降低，画面会越来越卡，重启光猫和路由器后恢复正常

演示视频：
https://www.bilibili.com/video/BV1sd4y1R7J3/
