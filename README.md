Internet weather station for the Raspberry Pi

# Install

Install Python3:

sudo apt-get install python3

Install additional libraries:

sudo pip3 install numpy pillow spidev 

Get app sources:

git clone https://github.com/dmitryelj/RPi-Weather-Station.git

Get free key at https://openweathermap.org/api (press "Subscribe" on this page). Save key as "key.txt" in the app folder.

Add app to startup (sudo nano /etc/rc.local):

python3 /home/pi/Documents/RPi-Weather-Station/weather.py &

Thats it.

# Screenshots
![View](/screenshots/Meteo01.jpg)

