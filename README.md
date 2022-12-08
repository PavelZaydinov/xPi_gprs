# xPi_gprs

This application is designed to forward incoming SMS messages and send notifications about an incoming call. 
OrangePi 4 LTS and GPRS Shield Arduino UNO are used as hardware. The interaction of the boards is carried out by
means of the UART4 port built into the Orange Pi. Incoming messages and notifications are forwarded to Telegram. 
The application consists of two small services. The first is responsible for working with the GPRS Shield module 
Arduino UNO Sim900, and the second for sending messages to Telegram. Sending is made by a separate service for 
the possibility of using it by third-party applications such as Asterisk. Data is exchanged between the services 
via the HTTP protocol using the JSON format.

Installing the app
------------

An installation example will be described for OrangePi 4 LTS Debian Bullseye Linux 5.10.43.
> The application can be run without problems on Raspberry Pi and on a regular PC. 
> For RaspberryPi, it is necessary to determine the gpio output to turn on and specify the serial port, 
> and for a PC, only the serial port, and remove the power output in the environment variables.

First, install the necessary packages:
```shell
apt update && apt -y upgrade && apt -y install docker docker-compose docker.io 
```
OrangePi 4 for SPI1 and UART4 uses the same connection pins. By default, SPI1. To redefine,
you need to edit the file `/boot/orangepiEnv.txt` adding a line:
```text
overlays=uart4
```
**Reboot** orangepi and check for the presence of the ttyS4 port with the command :
```shell
ls /dev/ttyS4
```
Next, install the library to work with gpio :
```shell
git clone https://github.com/orangepi-xunlong/wiringOP

cd wiringOP
./build clean
./build
```
The pin matching table can be output with the command:
```shell
gpio readall
```
The output should look something like this:
```text
 +------+-----+----------+------+---+OPi 4 LTS +---+---+--+----------+-----+------+
 | GPIO | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | GPIO |
 +------+-----+----------+------+---+----++----+---+------+----------+-----+------+
 |      |     |     3.3V |      |   |  1 || 2  |   |      | 5V       |     |      |
 |   64 |   0 | I2C8_SDA | ALT2 | 1 |  3 || 4  |   |      | 5V       |     |      |
 |   65 |   1 | I2C8_SCL | ALT2 | 1 |  5 || 6  |   |      | GND      |     |      |
 |  150 |   2 |     PWM1 |   IN | 0 |  7 || 8  | 1 | ALT2 | I2C3_SCL | 3   | 145  |
 |      |     |      GND |      |   |  9 || 10 | 1 | ALT2 | I2C3_SDA | 4   | 144  |
 |   33 |   5 | GPIO1_A1 |  OUT | 0 | 11 || 12 | 1 | IN   | GPIO1_C2 | 6   | 50   |
 |   35 |   7 | GPIO1_A3 |  OUT | 1 | 13 || 14 |   |      | GND      |     |      |
 |   92 |   8 | GPIO2_D4 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO1_C6 | 9   | 54   |
 |      |     |     3.3V |      |   | 17 || 18 | 0 | IN   | GPIO1_C7 | 10  | 55   |
 |   40 |  11 | SPI1_TXD | ALT2 | 1 | 19 || 20 |   |      | GND      |     |      |
 |   39 |  12 | SPI1_RXD | ALT2 | 1 | 21 || 22 | 0 | IN   | GPIO1_D0 | 13  | 56   |
 |   41 |  14 | SPI1_CLK | ALT3 | 1 | 23 || 24 | 1 | ALT3 | SPI1_CS  | 15  | 42   |
 |      |     |      GND |      |   | 25 || 26 | 0 | IN   | GPIO4_C5 | 16  | 149  |
 +------+-----+----------+------+---+----++----+---+------+----------+-----+------+
 | GPIO | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | GPIO |
 +------+-----+----------+------+---+OPi 4 LTS +---+---+--+----------+-----+------+
```
To connect to the GPRS Shield, wPi 11 and 12 (tx, rx) will be used, to 7 and 8 (tx, rx) on the GPRS Shield. 
GND can be connected to any, and the power supply is 5V.
> After connecting the module, the consumed flow will increase by about 60 mA, 
> in the active state of the GPRS Shield (when starting up to 100 mA). 
> It is better to specify the exact consumption in the documentation for the board.

Next, we transfer wPi 5 to the recording mode (out) and work via sysfs :
```shell
gpio export 5 out
```
>It is not necessary to install the wiringOP library. To configure the wPi 5 port, you need to do the following, 
>first we export the port with the command:
> 
> `echo 33 > /sys/class/gpio/export`
> 
>The directory `/sys/class/gpio/gpio33/` should appear in which we edit the `direction` file to switch to 
>recording mode:
> 
> `echo out > /sys/class/gpio/gpio33/direction`
>
>then we can set the value in the file `/sys/class/gpio/gpio33/value` 1 or 0.

The preparatory work is completed, you can install the application. Download the app :
```shell
git clone https://github.com/PavelZaydinov/xPi_gprs.git

cd xPi_gprs
```
Change the file name env_file.env.example to env_file.env and edit it:
```shell
mv env_file.env.example  env_file.env 
vim env_file.env
```
```text
API_HOST=http://ssm
TTY_S=/dev/ttyUSB0
PWRBTN=/dev/pwrbtn

TG_TOKEN=123456789:234567890qwertyuiopASDFG_ZXCV56789
TG_CHAT_ID=123456789
PG_HOST=PGSQL_SERVER
PG_USER=nextcloud
PG_PASSWORD=nextcloud_password
PG_DB=nextcloud
```
For orangepi, the first three variables can be left unchanged. In TG_TOKEN we specify the Telegram bot token, 
TG_CHAT_ID we specify the chat id to which to forward the information. The remaining four variables are needed 
to connect to the nextcloud database, where the forwarding service checks for the presence of a phone number in 
contacts.
>Number verification can be disabled or changed by changing the `get_contact_name` function in the file `ssm_server.py`

After editing the environment variables, launch the application:
```shell
docker-compose up -d
```

That's it.