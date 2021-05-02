# -*- coding: utf-8 -*-
"""
Created on Sun May  2 22:46:06 2021

@author: mehme
"""

from btcturk_api.client import Client
from datetime import datetime, timedelta
from matplotlib import pyplot
import matplotlib.pyplot as plt, mpld3
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, Button, Cursor
import numpy as np
import math
import time
import os, sys
import threading


def linearRegration(liste):
    xs = liste[0]
    ys = liste[1]
    # print(liste)
    xOrt = np.mean(xs)
    yOrt = np.mean(ys)
    xMinusXOrt = [(x - xOrt) for x in xs]
    yMinusYOrt = [(y - yOrt) for y in ys]
    xMinusXOrtSquare = list(np.square(xMinusXOrt))
    xMinusXOrt_X_yMinusYOrt = [(xMinusXOrt[i] * yMinusYOrt[i]) for i in range(len(yMinusYOrt))]
    b1 = (np.sum(xMinusXOrt_X_yMinusYOrt)) / (np.sum(xMinusXOrtSquare))
    b0 = yOrt - (xOrt * b1)
    # y = b0 + b1*x
    # x = (y-b0)/b1
    return (b0,b1)

def topLRandBottomLR(liste):
    b0,b1 = linearRegration(liste)
    xs = liste[0]; ys = liste[1]
    tUpX, tUpY = [], []
    tBtX, tBtY = [], []
    for i in range(len(xs)):
        fy = lambda x: b0 + b1*x
        yi = fy(xs[i])
        if ys[i] >= (yi):  # doğrunun üstünde ise
            tUpX.append(xs[i])
            tUpY.append(ys[i])
        else:  # doğrunun altındaysa
            tBtX.append(xs[i])
            tBtY.append(ys[i])
    # print(((tUpX, tUpY), (tBtX, tBtY)))            
    return ((tUpX, tUpY), (tBtX, tBtY))
# x değerler ve y değerlerinı alır
# bunların orta çizgisinin altındaki ve üstündeki noktaların listesini döndürür
# sonra üsttekilerin ve alttakilerin ayrı ayrı orta çizgilerini alıp bunlarında 
# alındaki ve üstündeki değerleri ni kaydeder # bu sürec verilen "deger" değeri kadar devam eder.
def lrRanger(xV, yV, deger):
    xV_up, yV_up = xV, yV
    xV_bt, yV_bt = xV, yV
    
    for i in range(deger):
        ustANDalt_up = topLRandBottomLR([xV_up, yV_up])
        # yukarı değerler
        xV_up = ustANDalt_up[0][0]
        yV_up = ustANDalt_up[0][1]
        # alt değerler
        ustANDalt_bt = topLRandBottomLR([xV_bt, yV_bt])
        xV_bt = ustANDalt_bt[1][0]
        yV_bt = ustANDalt_bt[1][1]

    lineUP = linearRegration([xV_up, yV_up])
    lineBT = linearRegration([xV_bt, yV_bt])
    return lineUP, lineBT # fonksiyonunun sabit ve x'in katsayısını döndürür

my_client = Client()

fig = plt.figure(figsize=(20, 10))
nrowsNumber = 2
ncolsNumber = 2
gs = gridspec.GridSpec(nrows=nrowsNumber, ncols=ncolsNumber, height_ratios=[2,2],width_ratios=[2,2])

x_data, y_data = [], []
xLR, yLR = [], []
yatayX, yatayY = [], []



grafikDict = {}

sureler = [900, 1800, 3600, 86400] # sn

sycSure = 0
for nc in range(ncolsNumber):
    for nr in range(nrowsNumber):
        grafik = fig.add_subplot(gs[nc,nr])
    
        # axList.append(axN)
        LineN = grafik.plot_date([], [], "-")
        LineLR = grafik.plot_date([], [], "-")
        yatayLineN = grafik.plot_date([], [], "-")
        lineUP = grafik.plot_date([], [], "-")
        lineBT = grafik.plot_date([], [], "-")
        grafikCizgileri = [LineN,LineLR,yatayLineN,lineUP,lineBT]
        grafikBilgileri = [sureler[sycSure], grafikCizgileri] 
        sycSure+=1
        # axListLines.append(ListLines)
        axDict = {grafik: grafikBilgileri}
        grafikDict.update(axDict)
        
        

proccesTimeList = [] # get, # draw

bitconType = "ETH_TRY"

def karzararAlan(alimFnc, satisFnc, xValues, islemMiktarı = 1000, karYuzdesi= 1):
    fy = lambda b0, b1, x: b0 + b1*x
    KomisyonYuzdesi = 0.18
    fcommi = lambda miktar: miktar*(KomisyonYuzdesi/100)
    # ilk çigi [(x1, y1),(x2, y2)], son çizgi [(x1, y1),(x2, y2)]
    # rs = [[(x1, y1),(x2, y2)], [(x1, y1),(x2, y2)]]
    karAreaValues = [[],[]] 
    zararAreaValues = [[],[]]
    syc1 = 0
    syc2 = 0
    for x in xValues:
        satY = fy(satisFnc[0],satisFnc[1] ,x)
        alY = fy(alimFnc[0],alimFnc[1] ,x)
        alis = alY/(islemMiktarı - fcommi(islemMiktarı)) # etc 
        satis = fcommi((alis*satY)) + (alis*satY)
        # ilkKaredilebiliraralıkDeğeri = ikad
        ikad = 0
        # ilkZararEdilenaralıkDeğeri = izad
        izad = 0
        print(f"karOranı: {(((satis/islemMiktarı)-1)*100)}")
        if (((satis/islemMiktarı)-1)*100) >= karYuzdesi:
            # karYüzdesini karşılayan alan noktaları
            if syc1 == 0:
                syc1 +=1
                syc2 = 0
                ikad = satY - alY
                alXY, satXY= (x, alY), (x, satY)
                if zararAreaValues[-1]: # boş değilse
                    karAreaValues[0] = zararAreaValues[-1]
                else:
                    karAreaValues[0] = [alXY, satXY]
            else:
                if (satY-alY) >= ikad:
                    ikad = satY - alY
                    karAreaValues[-1] = [alXY, satXY]  
        else:
             if syc2 == 0:
                syc2 += 1
                syc1 = 0
                izad = satY - alY
                alXY, satXY= (x, alY), (x, satY)
                if karAreaValues[-1]: # boş değilse
                    zararAreaValues[0] = karAreaValues[-1]
                else:
                    zararAreaValues[0] = [alXY, satXY]
             else:
                if (satY-alY) >= izad:
                    izad = satY - alY
                    zararAreaValues[-1] = [alXY, satXY]
    return karAreaValues, zararAreaValues
             
def kesisiyorMu(fnc1, fnc2, x_dataInput, y_dataDraw):
    # grafik alanı içerisinde kesişiyor mu?
    f1b0, f1b1 = fnc1[0], fnc1[1]
    f2b0, f2b1 = fnc2[0], fnc2[1]
    # yf1 = f1b0 + f1b1*x = 0
    xf1 = (-f1b0)/f1b1
    xf2 = (-f2b0)/f2b1
    finalX = xf1+xf2
    # yf1 = f1b0 + f1b1*xf2
    # yf2 = f2b0 + f2b1*xf1
    # if yf1 == yf2:
    #     finalY = yf1
        
    resultX = False
    # resultY = False
    sonuc = False
    if (x_dataInput[0] < finalX) and (finalX < x_dataInput[-1]):
        resultX = True
    # if (y_dataDraw[0] < finalY) and (finalY < y_dataDraw[-1]):
    #     resultY = True
    # if (resultX and resultY):
    #     sonuc = True
    return resultX
    
    
    

def proccesTime(func):
    def inner(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        islemSuresi = int((time.time() - t)*1000)
        proccesTimeList.append(islemSuresi)
        return result
    return inner
   
@proccesTime       
def getData():
    global bitconType
    data = my_client.tick(bitconType)
    return data


syc = 0
startTime = datetime.now()
yLR = None

@proccesTime 
def draw(grafik, x_data, y_data,y):
    global startTime, syc
    grafikBilgileri = grafikDict[grafik]
    grafik.cla()
    # LineN = grafik.plot_date([], [], "-")
    # LineLR = grafik.plot_date([], [], "-")
    # yatayLineN = grafik.plot_date([], [], "-")
    # lineUP = grafik.plot_date([], [], "-")
    # lineBT = grafik.plot_date([], [], "-")
    
    sure = grafikBilgileri[0]
    x_dataDraw = x_data
    y_dataDraw = y_data
    
    gecensure = (datetime.now() - startTime).seconds
    if gecensure >= sure: 
        # son 'sure' sn içerisinde olan x değerleri
        x_dataDraw = list(filter(lambda x: (datetime.now() - x).seconds <= sure, x_dataDraw)) 
        y_dataDraw = y_dataDraw[-len(x_dataDraw):] # ve onlara karşılık gelen son y değerleri
        startTime = x_data[0]
    
    grafik.plot_date(x_dataDraw, y_dataDraw, "-")
    average = round((np.sum(y_dataDraw)/len(y_dataDraw)),2)
    maxY, minY = round(np.max(y_dataDraw)), round(np.min(y_dataDraw))
    
    
    if syc >= 100:
        yatayX = [x_dataDraw[0], x_dataDraw[-1]]
        yatayY = [y_dataDraw[-1], y_dataDraw[-1]]
        
        x_dataInput = [a.timestamp() for a in x_dataDraw]
        # linear Regration - ortalama çizgisi
        valuesLR = linearRegration([x_dataInput, y_dataDraw])
        b0, b1 = valuesLR[0], valuesLR[1]
        ortaXb1 = b1
        x1, x2 = startTime.timestamp(), datetime.now().timestamp()
        
        yCalc = lambda y: (b0 + b1*y)
        
        yLR = [yCalc(x1), yCalc(x2)]
        xLR = [startTime, datetime.now()]   
        # LinearRegration cizgisi
        grafik.plot_date(xLR, yLR, "-")
        # Anlık Gösterge cizgisi
        grafik.plot_date(yatayX, yatayY, "-")
         
        altFnc, satFnc = lrRanger(x_dataInput,y_dataDraw,2)
        # herhangi bir değer isnan ise çalışmasın = isnan
        isNanlist = altFnc[0], altFnc[1], satFnc[0], satFnc[1]
        isnan = float("nan")
   
        if isNanlist.count(isnan) == 0:
            
            fy = lambda b0, b1, x: b0 + b1*x
            xDegerleri = yatayX
            # alYDegerleri = [fy(altFnc[0], ortaXb1, x_dataInput[0]),
            #                 fy(altFnc[0], ortaXb1, x_dataInput[-1])]
            # satYDegerleri = [fy(satFnc[0],ortaXb1, x_dataInput[0]), 
            #                  fy(satFnc[0],ortaXb1, x_dataInput[-1])]
            alYDegerleri = [fy(altFnc[0], altFnc[1], x_dataInput[0]),
                            fy(altFnc[0], altFnc[1], x_dataInput[-1])]
            satYDegerleri = [fy(satFnc[0],satFnc[1], x_dataInput[0]), 
                              fy(satFnc[0],satFnc[1], x_dataInput[-1])]
                
            ## üst satma çizgisi    
            grafik.plot_date(xDegerleri, alYDegerleri, "-")    
            ## alt satın alma çizgisi
            grafik.plot_date(xDegerleri, satYDegerleri, "-") 
            # y1 , y2 = alYDegerleri, satYDegerleri
            # xVboth = [x_dataDraw[0], x_dataDraw[-1]]
            y1 , y2 = np.array(alYDegerleri), np.array(satYDegerleri)
            xVboth = np.array([x_dataDraw[0], x_dataDraw[-1]])
            if not kesisiyorMu(altFnc, satFnc,x_dataInput,y_dataDraw):
                karAreaValues, zararAreaValues = karzararAlan(altFnc, satFnc, x_dataInput)
                if (karAreaValues[0] and karAreaValues[-1]):
                    # ilk çigi [(x1, y1),(x2, y2)], son çizgi [(x1, y1),(x2, y2)]
                    # rs = [[(x1, y1),(x2, y2)], [(x1, y1),(x2, y2)]]
                    # rs[0][0][0] = rs[0][1][0]
                    # rs[-1][0][0] = rs[-1][1][0]
                    y1 = np.array([karAreaValues[0][0][1], karAreaValues[-1][0][1]])
                    y2 = np.array([karAreaValues[0][1][1], karAreaValues[-1][1][1]])
                    xForBoth = np.array(
                        datetime.fromtimestamp(karAreaValues[0][0][0]), 
                        datetime.fromtimestamp(karAreaValues[-1][0][0])
                        )
                    grafik.fill_between(xForBoth, 
                                        y1 , 
                                        y2, 
                                        where=(y1 > y2), 
                                        color='green', 
                                        alpha=0.3, 
                                        interpolate=True
                                        )
                    grafik.fill_between(xForBoth, 
                                        y1 , 
                                        y2, 
                                        where=(y1 < y2),  
                                        facecolor="none", 
                                        hatch="X", edgecolor="b", 
                                        linewidth=0.0, alpha=0.3, 
                                        interpolate=True)
                    
                if (zararAreaValues[0] and zararAreaValues[-1]):
                    y1 = np.array([zararAreaValues[0][0][1], zararAreaValues[-1][0][1]])
                    y2 = np.array([zararAreaValues[0][1][1], zararAreaValues[-1][1][1]])
                    xForBoth = np.array(
                        datetime.fromtimestamp(zararAreaValues[0][0][0]), 
                        datetime.fromtimestamp(zararAreaValues[-1][0][0])
                        )
                    grafik.fill_between(xForBoth, 
                                        y1 , 
                                        y2, 
                                        where=(y1 > y2), 
                                        color='red', 
                                        alpha=0.3, 
                                        interpolate=True
                                        )
                    grafik.fill_between(xForBoth, 
                                        y1 ,
                                        y2, 
                                        where=(y1 < y2), 
                                        facecolor="none",
                                        hatch="X", 
                                        edgecolor="b", 
                                        linewidth=0.0, 
                                        alpha=0.3, 
                                        interpolate=True)
                    
        
        
        
    minX = datetime.fromtimestamp((x_dataDraw[0].timestamp()-10))
    maxX = datetime.fromtimestamp((x_dataDraw[-1].timestamp()+10))
    
    grafik.set_ylim(np.min(y_dataDraw)-10,np.max(y_dataDraw)+10)
    grafik.set_xlim(minX,maxX)

    titleMsg = f"avg:{average}|mx:{maxY}|mn:{minY}|dT:"
    # grafik.set_xlabel()
    # fig.autofmt_xdate()
    return titleMsg, sure
    
    
    
def update(frame):
    global syc, yLR, x_data, y_data, proccesTime, grafikDict, bitconType, proccesTimeList

    data = getData()
    y = data[0]["last"]
    y_data.append(y)
    x_data.append(datetime.now())
    
    for grafik in grafikDict: 
        titleMsg, sure = draw(grafik, x_data, y_data,y)
        drawTime = proccesTimeList[-1]
        grafik.set_title(f"{sure/60}dk|{y}|{titleMsg}[{drawTime}]ms", fontsize=12)
        # getTime, drawTime, drawTime , drawTime, drawTime 

    getTime = proccesTimeList[-5]    
    fig.canvas.set_window_title(f"{bitconType} {y} ({getTime}) ms")
    syc +=1
    
    return 

# plt.subplots_adjust(left=0.25, bottom=0.25)
# axcolor = 'lightgoldenrodyellow'
# init_frequency = 3

# # # Make a horizontal slider to control the lrRanger.
# axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
# freq_slider = Slider(
#     ax=axfreq,
#     label='lrRanger',
#     valmin=1,
#     valmax=6,
#     valinit=init_frequency,
# )

# /api/v2/ticker requests are limited to 10 requests per 100 miliseconds. 100/10 = 10 maks request 

animation = FuncAnimation(fig, update, interval=10)


plt.show()



# tolerans oranının hesaplanması
# kar edilebilir bir açıklık ne kadar?
# anaPara = 1000
# komisyon = %0.18
# karYuzdesi = 2% olsun
# örn şimdi etc ne kadar = 24445.0 = etc
# bu fiyattan aldık diyelim

# commi = 1000*(0.18/100)
# etcAlınanMiktar = etc/(anaPara-commi)
# 102*(0.18/100) + 102
# lastEtcValue = ?
# satımTryMiktarı = ((etcAlınanMiktar*lastEtcValue))*(0.18/100) + (etcAlınanMiktar*lastEtcValue) TRY
# if ((satımTryMiktarı/anaPara-1)*100) == karYuzdesi:
    #acıklık = alımEtcValue - lastEtcValue
    #sat.....
    
    

# kar edilebilir bir açıklık değişim miktarı  ne kadar?
##### alım yapıldığındaki etc değeri ile satım yapıldığında istenilen kar oranını karşılayan etc değeri
#### 
    

# önce bir benim bütün hesap haretketlerimi getirelim btcTurk'ten orada ne olmuş ne bitmiş ona göre formulü ortaya çıkarırız.
