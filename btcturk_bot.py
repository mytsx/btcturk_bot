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
    xOrt = np.mean(xs)
    yOrt = np.mean(ys)
    xMinusXOrt = [(x - xOrt) for x in xs]
    yMinusYOrt = [(y - yOrt) for y in ys]
    xMinusXOrtSquare = list(np.square(xMinusXOrt))
    xMinusXOrt_X_yMinusYOrt = [
        (xMinusXOrt[i] * yMinusYOrt[i]) for i in range(len(yMinusYOrt))
    ]
    b1 = (np.sum(xMinusXOrt_X_yMinusYOrt)) / (np.sum(xMinusXOrtSquare))
    b0 = yOrt - (xOrt * b1)
    # y = b0 + b1*x
    # x = (y-b0)/b1
    # xValues = xs
    # yValues = [(b0 + b1 * x) for x in xs]
    return (b0,b1)

def topLRandBottomLR(liste):
    ortaCizgi = linearRegration(liste)
    xs = liste[0]; ys = liste[1]
    tUpX = [] ;tUpY = [];tBtX = [];tBtY = []
    for i in range(len(xs)):
        if ys[i] >= (
            ortaCizgi[2] + ortaCizgi[3] * xs[i]
        ):  # doğrunun üstündeki değerler
            tUpX.append(xs[i])
            tUpY.append(ys[i])
        else:  # doğrunun altındaki değerler
            tBtX.append(xs[i])
            tBtY.append(ys[i])

    return ((tUpX, tUpY), (tBtX, tBtY))

def lrRanger(xV, yV, deger):
    xV_up, xV_bt = xV, xV
    yV_up, yV_bt = yV, yV
    for i in range(deger):
        ustANDalt_up = topLRandBottomLR([xV_up, yV_up])
        # yukarı değerler
        xV_up = ustANDalt_up[0][0]
        yV_up = ustANDalt_up[0][1]
        # alt değerler
        ustANDalt_bt = topLRandBottomLR([xV_bt, yV_bt])
        xV_bt = ustANDalt_bt[1][0]
        yV_bt = ustANDalt_bt[1][1]

    lineUP = linearRegration(ustANDalt_up[0])
    lineBT = linearRegration(ustANDalt_bt[1])
    return lineUP, lineBT

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
    grafik.legend(["ETC-TRY", "LR", "Anlık Gösterge"])
    sure = grafikBilgileri[0]
    x_dataDraw = x_data
    y_dataDraw = y_data
    
    gecensure = (datetime.now() - startTime).seconds
    if gecensure >= sure: 
        # son 'sure' sn içerisinde olan x değerleri
        x_dataDraw = list(filter(lambda x: (datetime.now() - x).seconds <= sure, x_dataDraw)) 
        y_dataDraw = y_dataDraw[-len(x_dataDraw):] # ve onlara karşılık gelen son y değerleri
        startTime = x_data[0]
    
    grafikBilgileri[1][0][0].set_data(x_dataDraw, y_dataDraw)
    average = round((np.sum(y_dataDraw)/len(y_dataDraw)),2)
    maxY, minY = round(np.max(y_dataDraw)), round(np.min(y_dataDraw))
    
    
    if syc >= 10:
        yatayX = [x_dataDraw[1], x_dataDraw[-1]]
        yatayY = [y_dataDraw[-1], y_dataDraw[-1]]
        
        x_dataInput = [a.timestamp() for a in x_dataDraw]
        valuesLR = linearRegration([x_dataInput, y_dataDraw])
        b0, b1 = valuesLR[0], valuesLR[1]
        x1, x2 = startTime.timestamp(), datetime.now().timestamp()
        yCalc = lambda y: (b0 + b1*y)
        yLR = [yCalc(x1), yCalc(x2)]
        xLR = [startTime, datetime.now()]
        
        grafikBilgileri[1][1][0].set_data(xLR, yLR)
        grafikBilgileri[1][2][0].set_data(yatayX, yatayY)
        
    # grafikBilgileri[1][3][0].set_data() 
    # grafikBilgileri[1][4][0].set_data() 
    minX = datetime.fromtimestamp((x_dataDraw[0].timestamp()-10))
    maxX = datetime.fromtimestamp((x_dataDraw[-1].timestamp()+10))
    
    grafik.set_ylim(np.min(y_dataDraw)-10,np.max(y_dataDraw)+10)
    grafik.set_xlim(minX,maxX)

    titleMsg = f"avg = {average}, max = {maxY}, min =  {minY}, dT = "
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
        grafik.set_title(f"_{sure/60}dk_ {y}|, {titleMsg}[{drawTime}] ms")
        # getTime, drawTime, drawTime , drawTime, drawTime 

    getTime = proccesTimeList[-5]    
    fig.canvas.set_window_title(f"{bitconType} {y} ({getTime}) ms")
    syc +=1
    
    return 


# /api/v2/ticker requests are limited to 10 requests per 100 miliseconds. 100/10 = 10 maks request 
fig1, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
axcolor = 'lightgoldenrodyellow'
init_frequency = 3

# # Make a horizontal slider to control the lrRanger.
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
freq_slider = Slider(
    ax=axfreq,
    label='lrRanger',
    valmin=1,
    valmax=6,
    valinit=init_frequency,
)

animation = FuncAnimation(fig, update, interval=10)


plt.show()



