# Internet Weather Station for the Raspberry Pi and Adafruit Display
# Mady by Dmitrii dmitryelj@gmail.com
# v1.0b

import sys, os, threading, time
import math
import urllib
import utils
import geocoder
import numpy as np
from PIL import Image
from dataProvider import WeatherProviderOW
import libTFT

# Get key for free at https://openweathermap.org/api
# OpenWeather API key can be placed here, or in key.txt file
owKey = ""
updateIntervalInS = 120
latDefault, lonDefault = 56.376525, 8.901999

# UI digits
signs = [None] * 13
signsWidth = [0] * 13
signsHeight = [0] * 13

class UIMainView(object):
  def __init__(self):
    self.tft = libTFT.lcdInit()
    self.tft.clear_display(self.tft.WHITE)
    self.tft.led_on(True)

    self.initUI()

  def initUI(self):
      global signs, signsWidth, signsHeight
      
      files = [ "digit0.png", "digit1.png", "digit2.png", "digit3.png", "digit4.png",
                "digit5.png", "digit6.png", "digit7.png", "digit8.png", "digit9.png",
                "minus.png", "plus.png", "digitC.png" ]
      
      for p, name in enumerate(files):
          path = "{}{}ui{}{}".format(utils.getAppPath(), os.sep, os.sep, name)
          im = Image.open(path)
          width, height = im.size
          rgb_img = im.convert('RGB')
          signs[p] = rgb_img
          signsWidth[p]  = width
          signsHeight[p] = height

      margin = 26

      self.sign = libTFT.UIImage(signs[10], x=margin, y=5)
      self.tft.controls.append(self.sign)

      self.digit1 = libTFT.UIImage(signs[0], x=margin+50, y=5)
      self.tft.controls.append(self.digit1)

      self.digit2 = libTFT.UIImage(signs[0], x=margin+130, y=5)
      self.tft.controls.append(self.digit2)

      self.c = libTFT.UIImage(signs[12], x=margin+200, y=5)
      self.tft.controls.append(self.c)

      # Labels
      self.labelPressure = libTFT.UILabel("Pressure", 18,126, textColor=self.tft.BLACK, backColor=self.tft.WHITE, fontS = 7)
      self.tft.controls.append(self.labelPressure)
      self.labelRain = libTFT.UILabel("Rain", 270,126, textColor=self.tft.BLUE, backColor=self.tft.WHITE, fontS = 7)
      self.tft.controls.append(self.labelRain)

      # Graph Bar image
      xLeft = 16
      # 1px = 5min, W = 24*60/5 = 288px
      barImg = Image.new('RGB', (288,40), (200, 200, 200))
      self.barCtrl = libTFT.UIImage(barImg, x=xLeft, y=145)
      self.tft.controls.append(self.barCtrl)
      
      # Tick labels 24h
      for p in range(0,25):
        h1 = 60/5   # 1 hour = 60/5 = 12px
        self.tft.controls.append(libTFT.UILine(xLeft + h1*p, 184, xLeft + h1*p, 188, self.tft.BLACK))
        if p%3 == 0:
          dx = 3 if p <= 10 else 6
          self.tft.controls.append(libTFT.UILabel(str(p), xLeft + h1*p - dx, 190, self.tft.BLACK, self.tft.WHITE, fontS = 3))

      # Footer
      self.tft.controls.append(libTFT.UILine(0, 215, 320, 215, self.tft.GREY))
      self.labelIP = libTFT.UILabel("", 6,218, textColor=self.tft.BLACK, backColor=self.tft.WHITE, fontS = 7)
      self.tft.controls.append(self.labelIP)
      self.labelLastUpdate = libTFT.UILabel("", 216,218, textColor=self.tft.BLACK, backColor=self.tft.WHITE, fontS = 7)
      self.tft.controls.append(self.labelLastUpdate)


  def updateUI(self, weather):
        global signs, signsWidth, signsHeight
        try:
            signIndex = 10 if weather.temperature < 0 else 11
            self.sign.setImage(signs[signIndex])
            
            tempHi, tempLo = int(weather.temperature/10), int(weather.temperature%10)
            self.digit1.setImage(signs[tempHi])
            self.digit2.setImage(signs[tempLo])

            self.labelIP.text = "IP:" + utils.getIPAddress()
            self.labelLastUpdate.text = "Update:" + weather.lastUpdateStr if len(weather.lastErrorStr) == 0 else weather.lastErrorStr

        except BaseException as e:
            print("updateUI error:", str(e), sys.exc_info()[2].tb_lineno)

  def updatePressureBar(self, weather):
    try:
        # Create and draw to buffer image
        w, h = self.barCtrl.width, self.barCtrl.height
        data = np.full((h, w, 3), 255, dtype=np.uint8)
      
        # Draw bars
        pressureMin  = 900
        pressureHigh = 1050
        pressureNormal = 1013
        k = 0.6
        # Pressure graph
        for p, hpa in enumerate(weather.listPressure):
            if hpa == 0:
                data[h-1][p] = [150,150,150]
                data[h-2][p] = [150,150,150]
                continue
            
            val = int(k*(hpa - pressureMin))
            if val > 35: val = 35
            for y in range(h - val, h):
                data[y][p] = [200,200,200]
    
        # Normal pressure line
        for p in range(0,w):
            val = int(k*(pressureNormal - pressureMin))
            data[h - val][p] = [150,150,150]
    
        # Draw rains
        for p, value in enumerate(weather.listRains):
            if value == 0: continue
        
            # Value in mm (0.0 - 5.0) to color => bigger-darker
            val = int(100*value)
            if val > 30: val = 30
            for y in range(h - val - 2, h - 2):
                data[y][p] = [0,0,200]

        img_data = Image.fromarray(data, 'RGB')
        self.barCtrl.setImage(img_data)

    except BaseException as e:
        print("updatePressureBar error:", str(e), sys.exc_info()[2].tb_lineno)

  def draw(self):
      self.tft.draw()
  
  def mainloop(self):
      self.tft.mainloop()

  def coordinates2WmtsTilesNumbers(self, lat_deg, lon_deg, zoom):
      # Not implemented: display clouds
      # http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
      lat_rad = math.radians(lat_deg)
      n = 2.0 ** zoom
      xtile = int((lon_deg + 180.0) / 360.0 * n)
      ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
      return xtile, ytile

  def owMapLayerUrl(self, layer, zoom, tilex, tiley, apiKey):
      # Not implemented: display clouds
      # Sample: http://tile.openweathermap.org/map/clouds/15/5/6.png?appid=00000000
      return "http://tile.openweathermap.org/map/{}/{}/{}/{}.png?appid={}".format(layer, zoom, tilex, tiley, apiKey)

def getLocalCoordinates():
  try:
    g = geocoder.ip('me')
    lat = g.latlng[0]
    lon = g.latlng[1]
    print("Coordinates found:", lat, lon)
    return lat, lon
  except:
    print("Warning: cannot get coordinates")
    return latDefault, lonDefault

if __name__ == "__main__":

    print("Started")
    
    view = UIMainView()

    lat, lon = getLocalCoordinates()
    weather = WeatherProviderOW(owKey)

    threadStop = False
    
    def uiUpdateThread():
      time.sleep(1)
      print("uiUpdateThread started")
    
      while True:
          weather.getWeatherForCoords(lat, lon)
          weather.printForDebug()
            
          view.updateUI(weather)
          view.updatePressureBar(weather)
          view.draw()

          for p in range(updateIntervalInS):
              time.sleep(1)
              if threadStop:
                  print("uiUpdateThread stopped")
                  return
    
    thread = threading.Thread(target=uiUpdateThread)
    thread.start()

    view.mainloop()
    threadStop = True

    #view.tft.clear_display(view.tft.WHITE)

    print("Done")
