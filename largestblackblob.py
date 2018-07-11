# Untitled - By: wmy - 周二 7月 10 2018

import sensor,time,pyb,math,time
from pyb import Pin, Timer, LED, UART

#黑色点阈值
black_threshold = [(0, 64)]

#xy平面误差数据
err_x = 0
err_y = 0

#串口三配置
uart = UART(3, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)#设置灰度信息
sensor.set_framesize(sensor.QQVGA)#设置图像大小
sensor.skip_frames(20)#相机自检几张图片
sensor.set_auto_whitebal(False)#关闭白平衡
clock = time.clock()#打开时钟

while(True):
    clock.tick()
    img = sensor.snapshot()
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
        # Draw a rect around the blob.
        img.draw_rectangle(blobs[i][0:4]) # rect
        #用矩形标记出目标颜色区域
        img.draw_cross(blobs[i][5], blobs[i][6]) # cx, cy
        #在目标颜色区域的中心画十字形标记
