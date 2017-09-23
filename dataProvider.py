# Openweather wrapper
# Available data and API https://openweathermap.org/price
# Mady by Dmitrii dmitryelj@gmail.com

import pyowm
import sys
import utils
import datetime
import tzlocal

class WeatherProviderOW:
  def __init__(self, key):
    self.owm = pyowm.OWM(key if len(key) > 0 else self.getAPIKey())
    # Public available data
    self.temperature = 0
    self.pressure = 0
    self.lastUpdateStr = "-"
    self.lastErrorStr = ""
    self.accuracyInM = 5
    # All-day data array, according to accuracy
    self.listPressure = [0] * int(24*60/self.accuracyInM)
    self.listRains    = [0] * int(24*60/self.accuracyInM)
    self.listRainTimes = []
    self.listRainValues = []

  def getAPIKey(self):
      try:
          if utils.isFileExist(utils.getAppPath() + 'key.txt'):
              with open(utils.getAppPath() + 'key.txt', 'r') as keyFile:
                  key = keyFile.read().replace('\n', '')
                  return key
      except BaseException as e:
          pass

      return ""
  
  def getWeatherHistory(self, lat, lon):
    try:
      # This call does not work with free OW key
      dtNow = datetime.datetime.now(tzlocal.get_localzone())
      dtStart = datetime.datetime(dtNow.year, dtNow.month, dtNow.day, tzinfo=dtNow.tzinfo)
      print("Request previous weather from:", dtStart, "to", dtNow)
      data = self.owm.weather_history_at_coords(lat, lon, dtStart, dtNow)
      print("History:", data)
      # TODO: add parsing and fill listPressure array
    except BaseException as e:
      print("getWeatherHistory error:", str(e))

  def getWeatherForCoords(self, lat, lon):
    self.lastErrorStr = ""
    try:
      observation = self.owm.weather_at_coords(lat, lon)
      w = observation.get_weather()
      dtRef = w.get_reference_time(timeformat='date')
      dtLocal = utils.dateAsLocalTZ(dtRef)
      
      self.lastUpdateStr = utils.dateAsString(dtRef, "%H:%M")
      
      # Temperature format: {'temp': 17.09, 'temp_max': 18.0, 'temp_min': 16.0, 'temp_kf': None}
      t = w.get_temperature('celsius')
      self.temperature = int(t['temp'])
      
      now = datetime.datetime.now()
      
      # Pressure format: {'sea_level': None, 'press': 1018}
      p = w.get_pressure()
      pval = int(p['press'])
      index = int((60*dtLocal.hour + dtLocal.minute)/self.accuracyInM)

      self.pressure = pval
      self.listPressure[index] = pval
      for p in range(index+1, len(self.listPressure)):
          self.listPressure[p] = 0
      
      # Forecast
      fc = self.owm.three_hours_forecast_at_coords(lat, lon)
      rain = fc.will_have_rain()
      snow = fc.will_have_snow()
      rains = fc.when_rain()
      for r in rains:
          dt = utils.dateAsLocalTZ(r.get_reference_time('date'))
          # Show only rains for today
          if dtRef.month != dt.month or dtRef.day != dt.day: continue
          
          index = int((60*dt.hour + dt.minute)/self.accuracyInM)
          value = r.get_rain()['3h']
      
          self.listRains[index] = value
      #  print("R", r.get_rain(), r.get_reference_time('date'))
      self.listRainTimes  = list(map(lambda r: utils.dateAsString(r.get_reference_time(timeformat='date'), "%Y-%m-%d %H:%M:%S"), rains))
      self.listRainValues = list(map(lambda r: r.get_rain()['3h'], rains))
      
      return True
    except BaseException as e:
      print("getWeatherForCoords error:", str(e), sys.exc_info()[2].tb_lineno)
      self.lastErrorStr = str(e)
      return False

  def printForDebug(self):
    try:
      print("Weather last update", self.lastUpdateStr)
      print("Temperature:", self.temperature)
      print("Pressure:", self.pressure)
      print("When rain:", self.listRainTimes)
      print("What rain:", self.listRainValues)
      print("List pressure:", self.listPressure)
      print("List rains:", self.listRains)
    except:
      pass

