Internet weather station for the Raspberry Pi

# Install

git clone https://github.com/dmitryelj/RPi-Weather-Station.git

Get free key at https://openweathermap.org/api (press "Subscribe"). Save key as "key.txt" in the app folder.

Install Python3:

sudo apt-get install python3

Install additional libraries:

sudo pip3 install numpy pillow spidev 

Add app to startup (sudo nano /etc/rc.local):

python3 /home/pi/Documents/RPi-Weather-Station/weather.py &

Thats it.

# Screenshots
![View](/screenshots/Meteo01.jpg)

