# -*- coding: utf-8 -*-
"""
Created on Mon May  3 17:42:13 2021

@author: mehme
"""
import numpy as np
from datetime import datetime

class Hesapla():
    def __init__(self):
        pass

    def linearRegration(self, liste):
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
    def topLRandBottomLR(self, liste):
        b0,b1 = self.linearRegration(liste)
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
    def lrRanger(self, xV, yV, deger):
        xV_up, yV_up = xV, yV
        xV_bt, yV_bt = xV, yV
        
        for i in range(deger):
            ustANDalt_up = self.topLRandBottomLR([xV_up, yV_up])
            # yukarı değerler
            xV_up = ustANDalt_up[0][0]
            yV_up = ustANDalt_up[0][1]
            # alt değerler
            ustANDalt_bt = self.topLRandBottomLR([xV_bt, yV_bt])
            xV_bt = ustANDalt_bt[1][0]
            yV_bt = ustANDalt_bt[1][1]
    
        lineUP = self.linearRegration([xV_up, yV_up])
        lineBT = self.linearRegration([xV_bt, yV_bt])
        return lineUP, lineBT # fonksiyonunun sabit ve x'in katsayısını döndürür
    def kesisiyorMu(self, fnc1, fnc2, x_dataInput = None, y_dataDraw = None, grafik = None):
        # 
        # print("kesisiyorMu fonkiyonu çalıştı...")
        # paralelse bu hesaba girmemeli
        # x'in katsayileri esit ise paralel olur y = b0 + b1*x
        if (fnc1[1] != fnc2[1]): # paralel degilse
            # satis [AB], alis[CD]
            b0f = fnc1[0] - fnc2[0]
            b1f = fnc2[1] - fnc1[1]
            eX = b0f/b1f
            eY = fnc1[0] + (fnc1[1]*eX)
            sonuc = eX, eY ###
        else:
            sonuc = 0 ### paralel
            # grafik alanı içerisinde kesişiyor mu?
        if x_dataInput: # x değerleri y değerleri ve grafik verileri verildiyse
            resultX = False
            resultY = False
            sonuc = False
            if (x_dataInput[0] < eX) and (eX < x_dataInput[-1]):
                resultX = True
            if (y_dataDraw[0] < eY) and (eY < y_dataDraw[-1]):
                resultY = True
            if (resultX or resultY):
                sonuc = True ###
                # print(eX, eY)
                grafik.plot_date(datetime.fromtimestamp(eX), eY)

        # print("######### sonuc #################")
        # print(sonuc)
        return sonuc
    
    def denklemiVer (self, nokta1, nokta2):
        # print("denklemiVer fonksiyonu çalıştı...")
        aX, aY = nokta1
        bX, bY = nokta2
        b1 = (aY-bY)/(aX-bX)
        # veya b0 = bY - b1*bX 
        b0 = aY - b1*aX 
        return b0, b1
    def noktaDogruParcasininUzerindeMİ(self, nokta, dogruParcasi):
        result = False
        d = dogruParcasi
        cX, cY = nokta
        if (d[0][0] <= cX) and (cX <= d[1][0]):
            result = True
        return result  
        
    def vurduMu(self, dogruParcasi, satFnc, alFnc):
        nokta1 = dogruParcasi[0] 
        nokta2 = dogruParcasi[-1]
        b0 , b1 = self.denklemiVer(nokta1, nokta2)
        # son iki noktadan geçen doğrunun deklemi = fnc
        fnc = b0, b1
        alHit = []
        satHit = []
        # alis fonksiyonu ile kesisiyor mu?
        resultA = self.kesisiyorMu(fnc, alFnc)
        resultS = self.kesisiyorMu(fnc, satFnc)
        
        if resultA !=0:# paralel değilse
            # bu nokta fnc üzerinde mi?
            # sonuc = eX, eY
            # kesisiyormu, kesişiyor ve o nokta son iki noktadan geçen doğru üzeirnde mi
            if self.noktaDogruParcasininUzerindeMİ(resultA, dogruParcasi):
                # bu nokta o doğrunun üzerinde yani alHit listesine ekle
                alHit.append(resultA)
        if resultS !=0:# paralel değilse
            # bu nokta fnc üzerinde mi?
            # sonuc = eX, eY
            if self.noktaDogruParcasininUzerindeMİ(resultS, dogruParcasi):
                # bu nokta o doğrunun üzerinde yani satHit listesine ekle
                satHit.append(resultS)
            
        # rFnc = lambda x, y  = ()
        
        return alHit, satHit
    def ortaNokta(self, fPoint, lPoint):
        # |AC|=|CB| ise x0= (x1+x2)/2 ve y0= (y1+y2)/2
        x1, x2  = fPoint[0], lPoint[0]
        y1, y2  = fPoint[1], lPoint[1]
        x0, y0 = (x1+x2)/2, (y1+y2)/2
        midPoint = x0, y0
        return midPoint
