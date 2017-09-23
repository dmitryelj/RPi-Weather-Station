# RPi-Weather-Station
Internet weather station for the Raspberry Pi

# Install

git clone https://github.com/dmitryelj/RPi-Weather-Station.git

Get free key at https://openweathermap.org/api (press "Subscribe"). Save key as "key.txt" in the app folder.

Add app to startup (sudo nano /etc/rc.local):

python3 /home/pi/Documents/Meteo/weather.py &

Thats it.

# Screenshots
![View](/screenshots/Meteo01.jpg)

