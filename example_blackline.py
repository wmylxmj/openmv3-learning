# blackline - By: Jinyuying - 周五 六月 2 2017
import sensor,time,pyb,math,time
from pyb import Pin, Timer, LED, UART
#黑色点阈值
black_threshold = [(0, 64)]
#高度数据
highcnt = 0.0
high = 0
#xy平面误差数据
err_x = 0
err_y = 0
#计数器
timercnt = 0
timerflag = 0
#发送数据
uart_buf = bytearray([0x55,0xAA,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                        0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xAA])
#超声波回调处理函数
def Ultrasound(line):
   if(Echo.value()==1):
        tim_count.init(prescaler=1799, period=2500)#打开定时器
   if(Echo.value()==0):
        global highcnt
        highcnt = tim_count.counter()#计数
        tim_count.deinit()
#发送函数
def tick(timer):
    uart.write(uart_buf)
#超声波发射端口配置
timpwm = Timer(4, freq=30) #超声波60赫兹发射频率
ch1 = timpwm.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width=80) #100us发射角
#超声波接收端口配置
tim_count = pyb.Timer(1) #定时器计数
extint = pyb.ExtInt('P0', pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_DOWN,Ultrasound)#开启外部中断
Echo = Pin('P0', Pin.IN, Pin.PULL_DOWN)
#timer发送配置
senddata = Timer(2, freq=60)
senddata.callback(tick)
#串口三配置
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)#设置灰度信息
sensor.set_framesize(sensor.QQVGA2)#设置图像大小
sensor.skip_frames(20)#相机自检几张图片
sensor.set_auto_whitebal(False)#关闭白平衡
clock = time.clock()#打开时钟
while(True):
    clock.tick()
    img = sensor.snapshot()
    high = int(1.7*highcnt)
    if(high>250):timerflag = 1
    else:
        timerflag = 0
        timercnt = 0
    #寻找blob
    blobs = img.find_blobs(black_threshold)
    if blobs:
        most_pixels = 0
        largest_blob = 0
        for i in range(len(blobs)):
            #目标区域找到的颜色块可能不止一个，找到最大的一个
            if blobs[i].pixels() > most_pixels:
                most_pixels = blobs[i].pixels()
                largest_blob = i
                if(timerflag == 1):timercnt = timercnt + 1
                #位置环用到的变量
                if(timercnt < 200):
                    [x,y,w,h]=blobs[largest_blob].rect()
                    err_x = int(64 - (x + w/2))
                    err_y = int(80 - y)
                else:
                    [x,y,w,h]=blobs[largest_blob].rect()
                    a = y+h
                    if(a == 159):
                        err_x = int(64 - (x + w/2))
                        err_y = -22
                    else:
                        err_x = int(64 - (x + w/2))
                        err_y = int(80 - (y + h))
    else:
       err_x = 0
       err_y = 0
    #数组中数据写入
    uart_buf = bytearray([0x55,0xAA,0x10,0x00,0x00,high>>8,high,err_x>>8,err_x,
                                err_y>>8,err_y,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xAA])
    #print(high)
