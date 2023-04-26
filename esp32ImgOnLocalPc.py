import cv2
import numpy as np 
import socket
import sys
import time
'''
这段代码运行在本地电脑上是被转发的对象
'''

IP="124.223.103.23" #在这里初始化你UDP服务器IP与端口
BINDPORT=8080
class esp32camera(object):
    def __init__(self):
        a=[]
        self.img = np.array(a, np.uint8) #创建空图片
        self.array = np.array(a, np.uint8)#创建空缓冲数组
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#建立一个UDP服务器
        self.server_address = (IP, BINDPORT)
        self.server_socket.sendto(b"LocalPc",self.server_address)
        self.server_socket.settimeout(30)
        cv2.namedWindow("fromserver", cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow("fromserver", 640, 480)
    def detectImg(self):#图像检测
        localtime = time.localtime(time.time())
        timeStr=time.strftime('%Y-%m-%d %H:%M:%S', localtime)
        cv2.putText(self.img, timeStr, (0, 30),cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 0), 1)
    def disPlayImg(self):#显示图像
        self.img = cv2.imdecode(np.array(bytearray(self.array), dtype='uint8'), cv2.IMREAD_UNCHANGED)#将数组转换img对象
        self.detectImg()
        try:
            cv2.imshow('fromserver', self.img)
        except:
            print("ERROR")
        k = cv2.waitKey(1)#等待按键 ESC退出
        if k == 27:
            self.server_socket.sendto(b"pcExit",self.server_address)
            self.server_socket.close()
            cv2.destroyAllWindows()
            sys.exit()
    def netWorkLoop(self):#死循环任务
        print("start")
        while True:
            receive_data, client_address = self.server_socket.recvfrom(50*1024)#接受数据
            #print("接收到了客户端 %s 传来的数据: %s\n" % (client_address, receive_data))
            print(client_address)
            self.array=np.append(self.array, receive_data[0:-1], axis=None)#添加数据到数组
            self.disPlayImg()#显示图片
            self.array = []#清空数组，准备下次接受
camera1 = esp32camera()
camera1.netWorkLoop()