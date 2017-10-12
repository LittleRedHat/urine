#!/bin/python
# -*- coding=utf-8 -*-
import cv2
import os
from skimage.measure import label,regionprops
import numpy as np
from collections import Counter
import math
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
import random
import sys
reload(sys)
sys.setdefaultencoding('UTF8')





class Urine():
    
    def __init__(self,image):
        self.image = image
        self.origin = np.copy(image)
        self.areaFilter = [450,10000]
        self.whRatio = [1.1,1.5]
        self.width2interval = 0.48649
        # self.redHsvRange = [[0,30],[300,360]]
        # self.greenHsvRange = [[90,150]]
        # self.blueHsvRange = [[210,270]]
        # self.yellowHsvRange = [[]]

        self.category = 8
        self.standard = standard_config
    
    def adjustGamma(self,image, gamma=1.0):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def preprocess(self):
        # self.image = self.adjustGamma(self.image,1.75)
        # cv2.imwrite('gamma.jpg',self.image)
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray,5)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,5)
        kernel = np.ones((3,3),np.uint8)
        cv2.dilate(thresh,kernel,iterations=2)
        self.gray = gray
        self.thresh = thresh

    def hemolysis(self,crop):
        gray = cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,9,5)
        kernel = np.ones((3,3),np.uint8)
        cv2.dilate(thresh,kernel,iterations=2)
        _,contours,hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            print area

        # cv2.imwrite('./hemo.jpg',thresh)
        
    def isAnchor(self,crop):

        width,height = crop.shape[1],crop.shape[0]
        step = width / 18
        left_section = crop[:,step:5*step,:]
        middle_section = crop[:,7 * step:11*step,:]
        right_section = crop[:,13*step:17*step,:]

        

        left_hsv = np.mean(cv2.cvtColor(left_section,cv2.COLOR_BGR2HSV)[:,:,0]) * 2
        middle_hsv = np.mean(cv2.cvtColor(middle_section,cv2.COLOR_BGR2HSV)[:,:,0]) * 2
        right_hsv = np.mean(cv2.cvtColor(right_section,cv2.COLOR_BGR2HSV)[:,:,0]) * 2

        # cv2.imwrite('left.jpg',left_section)
        # cv2.imwrite('middle.jpg',middle_section) 
        # cv2.imwrite('right.jpg',right_section)
    


        print left_hsv,middle_hsv,right_hsv

        flag = 0
        for item in self.blueHsvRange:
            if left_hsv > item[0] and left_hsv < item[1]:
                flag += 1
                break
        print flag
        for item in self.redHsvRange:
            if middle_hsv > item[0] and middle_hsv < item[1]:
                flag += 1
                break
        print flag

        for item in self.greenHsvRange:
            if right_hsv > item[0] and right_hsv < item[1]:
                flag += 1
                break
        print flag

        if flag == 3:
            return True

        return False
        # return flag

    def regionExtractByIndex(self,index):

        intervals = self.intervals
        widths = intervals



        leftStat = self.leftAnchorStat
        rightStat = self.rightAnchorStat

        leftCenter = leftStat['center']
        rightCenter = rightStat['center']
        distance = self.pointDistance(leftCenter,rightCenter)
        interval = (distance - widths * (leftStat['width'] + rightStat['width']) / 2.0) / intervals


        rect_width = (leftStat['width'] + rightStat['width']) / 2.0
        rect_height = (leftStat['height'] + rightStat['height']) / 2.0
        rect_angle = (leftStat['angle'] + rightStat['angle']) / 2.0
        theta = rect_angle * math.pi / 180.0 








        # d = (2 + index) * rect_width + index * interval

        # rect_center = (rightCenter[0] - d * math.cos(theta) , rightCenter[1] - d * math.sin(theta))

        # rect = (rect_center,(rect_width,rect_height),rect_angle)



        ratio = (index) * rect_width + (index) * interval


        ratio = ratio * 1.0 / (widths * rect_width + intervals * interval)

        rect_center = (leftCenter[0] * (1 - ratio) + rightCenter[0]* ratio , leftCenter[1] * (1 - ratio) + rightCenter[1] * ratio)

        rect = (rect_center,(rect_width,rect_height),rect_angle)



        # print '*'*40
        # print 'index is ',index
        # print 'interval is ',interval
        # print 'width is ',rect_width
        # print 'rect angle is ',rect_angle
        # print 'rect center is',rect_center
        # print 'ratio is ',ratio
        # print '*'*40
        return rect


        # anchor = self.anchor
        # anchorStat = self.anchorStat

        # support = self.support

        # center = anchorStat['center']

        # rect_width = anchorStat['width']
        # rect_height = anchorStat['height']
        # rect_angle = anchorStat['angle'] + 

        # theta =  rect_angle * math.pi / 180.0
        # ratio =  16.0 / 40.0
        # interval = rect_width * ratio

        # distance = (1 + 37.0 / 40.0 + index) * rect_width + index * interval

        # rect_center = (center[0] - distance * math.cos(theta) , center[1] - distance * math.sin(theta))

        # leftStat = self.leftStat
        # rightStat = self.rightStat
        # leftCenter = leftStat['center']
        # rightCenter = rightStat['center']

        # distance = self.pointDistance(leftCenter,rightCenter)
        
        # d = int(distance - leftStat['width'] / 2.0 - rightStat['width'] / 2.0 - rightStat['width'] / 3.0)

        # interval = (leftStat['width'] + rightStat['width'] ) / 6.0
        # rect_width = d * 1.0 / self.category - interval
        # rect_height = (self.leftStat['height'] + self.rightStat['height']) / 2.0
        # rect_angle = (self.leftStat['angle'] + self.rightStat['angle']) / 2.0

        # theta = rect_angle * math.pi / 180.0       
        # left_point = (leftCenter[0] + leftStat['width'] / 2.0 * math.cos(theta),leftCenter[1] + leftStat['width'] / 2.0 * math.sin(theta))
        # right_point = (rightCenter[0] - (rightStat['width'] / 2.0 + interval + rightStat['width'] / 3.0 ) * math.cos(theta),rightCenter[1] - (rightStat['width'] / 2.0 + interval + rightStat['width'] / 3.0) * math.sin(theta))
        # ratio =(index * interval) + (index - 0.5) * rect_width
        
        
        # ratio = ratio * 1.0 / (self.category * (interval + rect_width))
        # print 'index is ',index
        # print 'd is ',d
        # print 'ratio is ',ratio
        # print 'interval is ',interval
        # print 'left point is',left_point
        # print 'right point is ',right_point
       
        # rect_center = (left_point[0] * (1 - ratio) + right_point[0]* ratio , left_point[1] * (1 - ratio) + right_point[1] * ratio)
        
    def judgeDirection():
       
        leftStat = self.leftStat
        rightStat = self.rightStat
        leftCenter = leftStat['center']
        rightCenter = rightStat['center']

    def getRectPoints(self,src,rect):
        angle = rect[2]
        width,height = rect[1]
        center = rect[0]

        if angle < -45.0:
            angle += 90.0
            tmp = height
            height = width
            width = tmp
        
        m = cv2.getRotationMatrix2D(center,angle,1.0)
        size = (src.shape[1],src.shape[0])
        rotated = cv2.warpAffine(src,m,size)
        crop = cv2.getRectSubPix(rotated,(int(width),int(height)),center)
        return crop


    def locate(self): 
        # self.image = cv2.pyrMeanShiftFiltering(self.image,20,20)
        self.image = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
        self.image = cv2.pyrMeanShiftFiltering(self.image,10,10)
        self.image = cv2.cvtColor(self.image,cv2.COLOR_HSV2BGR)
        self.preprocess()

        # cv2.imwrite('binary.jpg',self.thresh)

        _,contours,hierarchy = cv2.findContours(self.thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        bboxs = []
        anchors = []
        anchors_indexs = []
        centers_x = []
        for index,cnt in enumerate(contours):
            # area filter
            area = cv2.contourArea(cnt)
            if area > self.areaFilter[1] or area < self.areaFilter[0]:
                continue
            stat = self.contourStat(cnt)

            # width / height filter
            if stat['wh_ratio'] > self.whRatio[1] or stat['wh_ratio'] < self.whRatio[0]:
                continue

            ##过滤掉候选框的内框
            if hierarchy[0][index][3] in anchors_indexs:
                continue
            anchors.append(cnt)
            anchors_indexs.append(index)
            centers_x.append(stat['center'][0])
            cv2.drawContours(self.image,[stat['box']],-1,(255,255,255),1)
            

        if len(anchors) < 2:
            return {'code':1001,'msg':'图片定位失败'}

        centers_x = np.array(centers_x)

        left_index = np.argmin(centers_x)
        self.leftAnchor = anchors[left_index]
        self.leftAnchorStat = self.contourStat(self.leftAnchor)

        right_index = np.argmax(centers_x)
        self.rightAnchor = anchors[right_index]
        self.rightAnchorStat = self.contourStat(self.rightAnchor)

        # inference for left and right interval
        leftCenter = self.leftAnchorStat['center']
        rightCenter = self.rightAnchorStat['center']

        distance = self.pointDistance(leftCenter,rightCenter)
        
        rect_width = (self.leftAnchorStat['width'] + self.rightAnchorStat['width']) / 2.0
       

        ratio = [abs(self.width2interval -  (distance / i - rect_width) / rect_width) for i in range(1,self.category)]
        self.intervals = ratio.index(min(ratio)) + 1
        
        # cv2.drawContours(self.image,[self.leftAnchorStat['box']],-1,(255,255,255),1)
        # cv2.drawContours(self.image,[self.rightAnchorStat['box']],-1,(255,255,255),1)

        anchors = []
        for i in range(self.category):
            rect =  self.regionExtractByIndex(i)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            anchors.append(rect)
            
        self.anchors = anchors
        # cv2.imwrite('./sss.jpg',self.image)
       

    

    def pointDistance(self,point1,point2):
        return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2))

    def contourStat(self,contour):
        # area for contour 
        area = cv2.contourArea(contour)
        # min area rotate rect
        rect = cv2.minAreaRect(contour)
        # rect center
        center = (int(rect[0][0]),int(rect[0][1]))

        width,height= rect[1][0],rect[1][1]

        angle = rect[2]

        if angle < -45.0:
            angle += 90
            tmp = height
            height = width
            width = tmp
        if width == 0:
            width = 1
        if height == 0:
            height = 1

        
        wh_ratio = width * 1.0 / height
        if wh_ratio < 1:
            wh_ratio =  1 / wh_ratio
        # four point for rotate rect
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        return {'angle':angle,'rect':rect,'area':area,'center':center,'width':width,'height':height,'wh_ratio':wh_ratio,'box':box}
        
    def colorDistance(self,lab1,lab2):
        color1 = LabColor(lab_l=lab1[0] / 255.0,lab_a = lab1[1],lab_b=lab1[2])
        color2 = LabColor(lab_l=lab2[0] / 255.0 ,lab_a = lab2[1],lab_b=lab2[2])
        return delta_e_cie2000(color1,color2)
    
    def colorCal(self,img):

        width,height = img.shape[1],img.shape[0]
        w_step = width / 4
        h_step = height / 4
        
        crop = img[h_step:3*h_step,w_step:3*w_step,:]
        lab = cv2.cvtColor(crop,cv2.COLOR_BGR2LAB)
        l_mean = np.mean(lab[:,:,0]) * 100 / 255
        a_mean = np.mean(lab[:,:,1]) - 128
        b_mean = np.mean(lab[:,:,2]) - 128
        
        return (l_mean,a_mean,b_mean)

    def run(self):
        r = self.locate()
        if r and r.get('code') and r.get('code') != 200:
            return r
        result = []
        for i,anchor in enumerate(self.anchors):

            crop = self.getRectPoints(self.origin,anchor)

            # cv2.imwrite('./rect-%d.jpg'%(i),crop)

            color = self.colorCal(crop)
            
            minDistance = 10000
            minStd = 0

            s = self.standard[i]
            for j,stanard in enumerate(s['items']):

                distance = self.colorDistance(color,stanard['lab'])
                if minDistance > distance:
                    minStd = stanard
                    minDistance = distance

            if minStd['index'] in s['normal'][0]:
                level = 0
            elif minStd['index'] in s['normal'][1]:
                level = 1
            else:
                level = 2

            result.append({'name':s['name'],'value':minStd['value'],'level':level})
        return result

def run():
    img = cv2.imread('./sample2.jpg')
    u = Urine(img)
    print u.run()
    
    



standard_dir = './standard'
standard_config = [
    {
        'name':u'潜血',
        'normal':[[0],[1,2],[3,4]],
        'values':['阴性','+-(10)','+(25)','++(80)','+++(200)'],
        'items':[]
    },{
        'name':u'亚硝酸盐',
        'normal':[[0],[1],[2]],
        'values':['阴性','+阳性','++强阳性'],
        'items':[]
    },{
        'name':u'pH',
        'normal':[[0,1,2],[],[3,4]],
        'values':['5.0','6.0','7.0','8.0','9.0'],
        'items':[]
    },{
        'name':u'尿胆原',
        'normal':[[0,1],[2],[3]],
        'values':['正常','正常','阳性','强阳性'],
        'items':[]
    },{
        'name':u'胆红素',
        'normal':[[0],[1,2],[3]],
        'values':['阴性','少量','中量','大量'],
        'items':[]
    },{
        'name':u'蛋白质',
        'normal':[[0],[1,2],[3,4,5]],
        'values':['阴性','trace','+(30)','++(100)','+++(300)','++++(2000)'],
        'items':[]
    },{
        'name':u'葡萄糖',
        'normal':[[0,1,2],[],[3,4]],'normal':[[0,1,2],[],[3,4]],
        'values':['阴性','+-(100)','+(250)','++(500)','+++(1000)','+++＋(2000)'],
        'items':[]
    },{
        'name':u'酮体',
        'normal':[[0,1,2],[],[3,4]],
        'values':['阴性','+-(5)','+(15)','++(40)','+++(80)','++++(160)'],
        'items':[],
    }
]

for item in os.listdir(standard_dir):
    name,ext = os.path.splitext(item)
    name = name.split('-')
    cat,index = name[0],name[1]
    value = standard_config[int(cat)-1]['values'][int(index)]
    img = cv2.imread(os.path.join(standard_dir,item))
    lab = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
    l_mean = np.mean(lab[:,:,0]) * 100 / 255
    a_mean = np.mean(lab[:,:,1]) - 128
    b_mean = np.mean(lab[:,:,2]) - 128
    lab_mean = (l_mean,a_mean,b_mean)
    standard_config[int(cat)-1]['items'].append({'index':int(index),'value':unicode(value),'lab':lab_mean})


if __name__ == '__main__':
    
    run()