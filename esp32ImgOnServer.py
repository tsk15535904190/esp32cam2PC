import sys #导入库
import cv2
import numpy as np 
import socket
import sys
import time
'''
这段代码运行于服务器或者局域网电脑
可以接受esp32 udp发送上来的图像数据
'''

IP="10.0.16.3" #在这里初始化你UDP服务器IP与端口
BINDPORT=8080
SAVEVIDEO=True
class esp32camera(object):
    def __init__(self):
        a=[]
        self.img = np.array(a, np.uint8) #创建空图片
        self.array = np.array(a, np.uint8)#创建空缓冲数组
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#建立一个UDP服务器
        self.address = (IP, BINDPORT)
        self.server_socket.bind(self.address)#服务器绑定IP与端口
        self.esp32_address = ('0.0.0.0',0) #ESP32的IP地址
        self.esp32Islog = False #ESP32登录标志位
        self.localPc_address = ('0.0.0.0',0)#需要转发的IP地址
        self.localPcIslog = False #本地PC登陆标志位
        self.__videoGap=10 #每间隔10张图片曲一张
        self.__videoCnt=0 
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('video.mp4',self.fourcc, 30.0, (640,480),True)
        cv2.namedWindow("fromesp32cam", cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow("fromesp32cam", 640, 480)
    def readFile(self,path,cnt):#该函数用来读取图片到数组，用来测试使用
        self.array = np.fromfile(path,dtype='uint8',count=cnt)
    def detectImg(self):#图像处理
        localtime = time.localtime(time.time())
        timeStr=time.strftime('%Y-%m-%d %H:%M:%S', localtime)
        cv2.putText(self.img, timeStr, (0, 30),
 			cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 0), 1)
        if SAVEVIDEO is True :
            if self.__videoGap ==self.__videoCnt:
                self.__videoCnt=0
                self.out.write(self.img)
            else :
                self.__videoCnt+=1
    def disPlayImg(self):#显示图像
        self.img = cv2.imdecode(np.array(bytearray(self.array), dtype='uint8'), cv2.IMREAD_UNCHANGED)#将数组转换img对象
        self.detectImg()
        try:
            cv2.imshow('fromesp32cam', self.img)
        except:
            print("error!")
        k = cv2.waitKey(1)
        if k == 27:
            print("exit")
            self.out.release()
            cv2.destroyAllWindows()
            sys.exit()
    def forwardPc(self,data): #转发给本地PC
        if self.localPcIslog is True :
            self.server_socket.sendto(data, self.localPc_address)
    def netWorkLoop(self):#死循环任务
        print("started!")
        while True:
            receive_data, client_address = self.server_socket.recvfrom(1401)#接受数据
            #print("接收到了客户端 %s 传来的数据: %s\n" % (client_address, receive_data))
            #print("接收到长度 %d 传来的数据最后一位: 0x%x\n" % (len (receive_data), receive_data[-1]))
            if  receive_data.decode("utf8","ignore")=="ESP32":#如果接收到“ESP32”,说明ESP32登陆了
                self.esp32_address = client_address
                print("ESP32摄像机登录@")
                print(self.esp32_address)
                continue
            if receive_data.decode("utf8","ignore")=="LocalPc":#如果接收到“LocalPc”,说明局域网电脑登陆了
                self.localPc_address = client_address
                self.localPcIslog = True
                print("PC登录@")
                print(self.localPc_address)
                #self.server_socket.sendto(b"A",self.esp32_address)#PC登陆后，发送给esp32开始拍照
                continue
            if receive_data.decode("utf8","ignore")=="pcExit":#接收到本地电脑退出，停止摄像头录像
                self.localPcIslog = False
                print("PC退出登录!")
                #self.server_socket.sendto(b"B",self.esp32_address)#PC退出登陆，发送给esp32停止拍照
                continue

            if receive_data[-1]!=0xFF :#0xFF代表一张图片的数据发送结束
                self.array=np.append(self.array, receive_data[0:-1], axis=None)#添加数据到数组
                self.esp32_address = client_address#接收到图像数据将地址保存
                continue
                #print("当前数组长度:%d" %(len(self.array)))
            else:
                self.array=np.append(self.array, receive_data[0:-1], axis=None)#添加最后一包数据
                self.forwardPc(self.array)#转发数据给电脑
                self.disPlayImg()#显示图片
                self.array = []#清空数组，准备下次接受
camera1 = esp32camera()
camera1.netWorkLoop()