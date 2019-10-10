**Client GUI for RaspberryPi robotic vehicle control system**
  ```
  Tested OK on Ubuntu 18.04LTS.
  Written in python3 with the help of Tk and pygame libraries.
  Tested OK with a Gamepad Logitech F310 controller
  ```
  
**Installation**

Step 1 - Setup local directory

Create a /rover directory and attribute ownership to the current user.

  ```
  $ sudo -s 
  $ cd /
  $ mkdir /rover
  $ chown <your user>:<your group> /rover
  $ exit
  ```

Step 2 - In /rover, clone this repo.

  ```
  $ cd /rover
  $ git clone https://github.com/raspberryrobot/clientcontrol
  ```
  
You should have these files in directory ```/rover/clientcontrol```
  ```
  Control.desktop
  README.md
  rover_client_GUI.py
  rover.conf
  ```
  
Step 3 - Set permissions for execution.

  ```
  $ cd ./clientcontrol
  $ chmod +x rover_client_GUI.py
  ```

Step 4 - Install required libraries and programs.

mplayer video software
  ```apt-get install -y mplayer```

Tkinter library
  ```apt-get install -y python3-tk```

Python3 package manager
  ```apt-get install -y python3-pip```

Latest version of pygame
  ```pip3 install pygame```

Latest version of tendo
  ```pip3 install tendo```
  
Step 5 - Configure for network access. 

In file rover.conf, set variable ROVER_IP with the IP address used by the Raspberry Pi controller.
  ```
  ROVER_IP = <Ipv4 address>
  ex: ROVER_IP = 192.168.99.1
  ```
  
Step 6 - Create a desktop shortcut

Copy file ```Control.desktop``` to your deskop. 
  ```
   $ cp /rover/clientcontrol/Control.desktop ~/Desktop
  ```

The operating system will create a graphic shortcut using this file.
Click [mark executable] when prompted at the initial execution.

  Control.desktop file content:
  
  ```
  [Desktop Entry]
  Version=1.0
  Type=Application
  Name=Control
  Comment=
  Exec=/rover/clientcontrol/rover_client_GUI.py
  Icon=transmission
  Path=/rover/clientcontrol/
  Terminal=false
  StartupNotify=false

  ```
 
**Basic Usage**

Buttons 
```
[start]         Start all user interface modules 
[stop]          Stop all user interface modules
[Ping rover]    Send ICMP request to RaspberryPi vehicle control instance
[Reboot]        Reboot RaspberryPi vehicle control instance
[Shutdown]      Shutdown RaspberryPi vehicle control instance
[Start control] Start user interface control module only
[Stop control]  Stop user interface control module only
[Start video]   Start user interface video module only
[Stop video]    Stop user interface video module only
[Exit]          Exit user interface program
```
Log windows

4 log windows are available

```
System log window               System command output
Control log - joystick          PS2 controller values     
Control log - motor telemetry   Motor remote telemetry
Video log - video data status   Video bytes received 
```
Video notes
```
The mplayer video program will start when at least 1M of data is received.
Mplayer may freeze (mplayer bug) if you click multiple time on the video screen. 
A complete restart of the GUI might be necessary to correct this. 

If you stop and restart the video module, wait at least 2-3 seconds to allow
the video server to reset and restart, otherwise you will get an error 
message
```
