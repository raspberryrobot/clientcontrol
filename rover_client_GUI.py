#!/usr/bin/python3

# ##############################################################################
#
# Libraries
#
# ##############################################################################

from tkinter import *           # GUI user interface
import socket                   # Network communication
import pygame                   # Joystick interface
import os                       # Operating system interface
import sys                      # System call 
import time                     # Time acquisition and formatting
import subprocess               # External process control
import threading                # Thread control
import psutil                   # Process and system monitoring
from tendo import singleton     # Mutex 

# ##############################################################################
#
# Global definitions
#
# ##############################################################################

# Thread control objects
RUN_CONTROL_THREAD = True
RUN_VIDEO_THREAD = True
RUN_TELEMETRY_THREAD = True
RUN_SUPERVISOR_THREAD = True

# Debug output flags
DEBUG_OUTPUT = True
DEBUG_CONTROL = True
DEBUG_VIDEO = True
DEBUG_TELEMETRY = True
DEBUG_SUPERVISOR = True
DEBUG_SYSTEM = True

# Configuration file name
ROVER_CONFIG_FILE = 'rover.conf'

# GUI settings
screen_height = 600
screen_width = 200
screen_x = 200
screen_y = 50
btn_width = 16
btn_heigth = 2
font_size = 10

# video player process id
player_pid = None

# ##############################################################################
#
# Functions
#
# ##############################################################################

# ##############################################################################
#
# Thread control functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# start_all_treads()
# ------------------------------------------------------------------------------
def start_all_treads():
    if DEBUG_OUTPUT: print("[MSG]> start all threads")
    start_control_thread()
    start_video_thread()
    start_telemetry_thread()

# ------------------------------------------------------------------------------
# stop_all_treads()
# -----------------------------------------------------------------------------
def stop_all_treads():
    if DEBUG_OUTPUT: print("[MSG]> stop all threads")
    stop_control_thread()
    stop_video_thread()
    stop_telemetry_thread()

# ##############################################################################
#
# Supervisor functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# stop_supervisor_thread()
# ------------------------------------------------------------------------------
def stop_supervisor_thread():
     global RUN_SUPERVISOR_THREAD
     if DEBUG_SUPERVISOR: print("[MSG]> stop supervisor thread")
     RUN_SUPERVISOR_THREAD=False

# ------------------------------------------------------------------------------
# start_supervisor_thread()
# ------------------------------------------------------------------------------
def start_supervisor_thread():
    if DEBUG_SUPERVISOR: print("[MSG]> start supervisor thread")
    t = threading.Thread(name='supervisor',target=start_supervisor, args=())
    t.daemon = True
    t.start()

# ------------------------------------------------------------------------------
# start_supervisor()
# ------------------------------------------------------------------------------
def start_supervisor():
    global RUN_SUPERVISOR_THREAD
    while True:
        if(RUN_SUPERVISOR_THREAD == False): sys.exit()
        for t in threading.enumerate():
            if (t.is_alive):
                if DEBUG_SUPERVISOR: print("[MSG]> {0} is alive".format(t.name))
        time.sleep(1)

# ##############################################################################
#
# Control functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# stop_control_thread()
# ------------------------------------------------------------------------------
def stop_control_thread():
    global RUN_CONTROL_THREAD
    global control_log
    if DEBUG_CONTROL: print("[MSG]> stop control thread")
    RUN_CONTROL_THREAD=False

# ------------------------------------------------------------------------------
# start_control_thread()
# ------------------------------------------------------------------------------
def start_control_thread():
    global ROVER_IP
    global ROVER_CONTROL_PORT
    global RUN_CONTROL_THREAD
    global control_log

    if DEBUG_CONTROL: print("[MSG]> start control thread")

    # update GUI information
    func_success_msg(control_log,"Control: started")

    # set control thread flag to true
    RUN_CONTROL_THREAD=True

    # start control thread
    t = threading.Thread(name='control',target=start_control, args=(0,ROVER_IP,ROVER_CONTROL_PORT,))
    t.daemon = True
    t.start()

# ------------------------------------------------------------------------------
# start_control(device_id,robot_ip,robot_port)
# ------------------------------------------------------------------------------
def start_control(device_id,robot_ip,robot_port):
    global RUN_CONTROL_THREAD
    global control_log
    global motor_log

    if DEBUG_CONTROL: print("[MSG]> start_control()")

    if (RUN_CONTROL_THREAD == False): sys.quit()

    # UDP_send_data(data,ip,port)
    def UDP_send_data(data,ip,port):
        error_code = 0
        data=data.encode()
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket.sendto(data,(ip,port))
        return error_code

    # data_to_pwm(axis_1,axis_2)
    def data_to_pwm(axis_1,axis_2):
        deviation = 0.01
        LF,LR,RL,RR = 0,0,0,0
        if axis_1 < 0:
            LF = abs(int (axis_1 * 100))
        elif axis_1 > 0:
            LR = abs(int ((axis_1 + deviation ) * 100))
        if axis_2 < 0:
            RL = abs(int (axis_2 * 100))
        elif axis_2 > 0:
            RR = abs(int ((axis_2 + deviation) * 100))
        return (LF,LR,RL,RR)

    # function main
    interference_level = 99
    LF,LR,RL,RR = 0,0,0,0

    # init pygame object
    pygame.init()
    pygame.joystick.init() # main joystick device system
    clock = pygame.time.Clock()

    # init joystick
    try:
        j = pygame.joystick.Joystick(device_id) # create a joystick instance
        j.init() # init instance
        if DEBUG_CONTROL: print("[JOY]> Enabled joystick: {}".format(j.get_name()))
    except pygame.error:
        if DEBUG_CONTROL: print("[JOY]> no joystick found.")
        func_error_msg(control_log,"Joystick error")

    try:
        # get user input and send to control server
        while RUN_CONTROL_THREAD:
            control_msg = ""
            # get button and hat events
            for e in pygame.event.get():
                if e.type == pygame.JOYHATMOTION:
                    hat_data = []
                    eventID = str(e.type)
                    hat_data.append(eventID)
                    hat_data.append(str(j.get_hat(0)[0]))
                    hat_data.append(str(j.get_hat(0)[1]))
                    control_msg = ",".join(hat_data)

                elif e.type == pygame.JOYBUTTONDOWN:
                    bd_data = []
                    eventID = str(e.type)
                    bd_data.append(eventID)
                    for button in range(0,12):
                        bd_data.append(str(j.get_button(button)))
                    control_msg = ",".join(bd_data)

                elif e.type == pygame.JOYBUTTONUP:
                    bu_data = []
                    eventID = str(e.type)
                    bu_data.append(eventID)
                    for button in range(0,12):
                        bu_data.append(str(j.get_button(button)))
                    control_msg = ",".join(bu_data)

            # send button and hat control values
            if control_msg != "":
                if DEBUG_CONTROL: print("[BTN]> {0}".format(control_msg))
                UDP_send_data(control_msg,robot_ip, robot_port)
                func_success_msg(control_log,control_msg)

            # get joystick values
            control_msg = ""
            left_j_value = 0
            right_j_value = 0
            left_j_value = j.get_axis(1)
            right_j_value = j.get_axis(2)

            # format joystick values as control message
            if (left_j_value or right_j_value):
                LF,LR,RL,RR=0,0,0,0
                LF,LR,RL,RR = data_to_pwm(left_j_value,right_j_value)
                if LF < interference_level: LF=0
                if LR < interference_level: LR=0
                if RL < interference_level: RL=0
                if RR < interference_level: RR=0
                control_msg = '7,{},{},{},{}'.format(LF,LR,RL,RR)

            # send joystick control message
            if control_msg != "":
                if DEBUG_CONTROL: print("[JOY]> {0}".format(control_msg))
                UDP_send_data(control_msg,robot_ip, robot_port)
                control_msg = "Control: " + str(control_msg)
                func_success_msg(control_log,control_msg)

            clock.tick(100)

    finally:
         func_error_msg(control_log,"Control: stopped")
         func_error_msg(motor_log,"Motor: no data")

# ##############################################################################
#
# Video functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# stop_video_thread()
# ------------------------------------------------------------------------------
def stop_video_thread():
    global RUN_VIDEO_THREAD
    global player_pid
    global video_log

    if DEBUG_VIDEO: print("[MSG]> stop video thread")

    # set video thread to False
    RUN_VIDEO_THREAD=False

    # kill stream player program
    try:
        if psutil.pid_exists(player_pid):
            if DEBUG_VIDEO: print("[MSG]> kill video player - pid: {}".format(player_pid))
            p = psutil.Process(int(player_pid))
            p.kill()
    finally:
        player_pid = None

# ------------------------------------------------------------------------------
# start_video_thread()
# ------------------------------------------------------------------------------
def start_video_thread():
    global ROVER_IP
    global ROVER_VIDEO_PORT
    global RUN_VIDEO_THREAD
    global video_log

    if DEBUG_VIDEO: print("[MSG]> start video thread")

    # update GUI information
    func_success_msg(video_log,"Video: started")

    # set video thread to True
    RUN_VIDEO_THREAD=True

    # start video thread
    t = threading.Thread(name='video',target=start_video, args=(ROVER_IP,ROVER_VIDEO_PORT))
    t.daemon = True
    t.start()

# ------------------------------------------------------------------------------
# start_video(robot_ip,robot_port)
# ------------------------------------------------------------------------------
def start_video(robot_ip,robot_port):
    global RUN_VIDEO_THREAD
    global tk_win
    global video_log
    global player_pid
    PKT_SIZE = 1024

    # stream player window information
    win_x = (tk_win.winfo_x() + 200)
    win_y = (tk_win.winfo_y() - 24)
    geometry_string = "{}:{}".format(win_x,win_y)

    # stream player command line
    #cmdline = ['mplayer','-fps','40','-geometry',geometry_string,'-xy', '800','-msglevel','all=-1','-cache','256','-']
    cmdline = ['mplayer','-fps','48','-geometry',geometry_string,'-xy', '800','-msglevel','all=-1','-nocache','-']

    if DEBUG_VIDEO: print("[MSG]> start_video()")

    if (RUN_VIDEO_THREAD == False): sys.quit()

    # check if rover is up
    if (func_icmp_echo_request(robot_ip) == -1):
        if DEBUG_VIDEO: print("[MSG]> error: network")
        func_error_msg(video_log,"Error: rover is down")
        return

    # connect to video server
    try:
        client_socket = socket.socket()
        client_socket.connect((robot_ip,robot_port))
        if DEBUG_VIDEO: print("[MSG]> success: connected to {}:{}".format(robot_ip,robot_port))
    except Exception as e:
        if DEBUG_VIDEO: print("[MSG]> X error: {}".format(str(e)))
        if DEBUG_VIDEO: print("[MSG]> error: not connected to {}:{}".format(robot_ip,robot_port))
        func_error_msg(video_log,"Error: socket connect")

    # recv data from video server and send player
    else:
        data_recv = 0
        try:
            # open video player
            player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
            player_pid = player.pid
            if DEBUG_VIDEO: print("[MSG]> player pid: {}".format(player_pid))

            while True:
                #receive data from video server
                data = client_socket.recv(PKT_SIZE)

                # check for video thread flag
                if(RUN_VIDEO_THREAD == False):
                    break
                else:
                    # calculate total amount of data received
                    data_recv += len(data)
                    if not data:
                        if DEBUG_VIDEO: print('[MSG]> error: connection closed')
                        func_error_msg(video_log,"Error: connection")
                        break

                    # send receive data to stream player
                    player.stdin.write(data)
                    func_success_msg(video_log,data_recv)

        except Exception as e:
            if DEBUG_VIDEO: print("[MSG]> error: {}".format(str(e)))
            func_error_msg(video_log,"Error: network")
        finally:
            player.terminate()
            client_socket.close()
            time.sleep(1)
            func_error_msg(video_log,"Video: channel closed")
            if DEBUG_VIDEO: print("[MSG]> video channel closed")

# ##############################################################################
#
# Telemetry functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# stop_telemetry_thread()
# ------------------------------------------------------------------------------
def stop_telemetry_thread():
    global RUN_TELEMETRY_THREAD
    if DEBUG_TELEMETRY: print("[MSG]> stop telemetry thread")
    RUN_TELEMETRY_THREAD = False

# ------------------------------------------------------------------------------
# start_telemetry_thread()
# ------------------------------------------------------------------------------
def start_telemetry_thread():
    global RUN_TELEMETRY_THREAD
    RUN_TELEMETRY_THREAD = True
    if DEBUG_TELEMETRY: print("[MSG]> start telemetry thread")
    t = threading.Thread(name='telemetry',target=start_telemetry, args=(ROVER_IP,ROVER_TELEMETRY_PORT,CLIENT_TELEMETRY_PORT))
    t.daemon = True
    t.start()

# ------------------------------------------------------------------------------
# start_telemetry()
# ------------------------------------------------------------------------------
def start_telemetry(robot_ip,robot_port,client_port):
    global RUN_TELEMETRY_THREAD
    global telemetry_log
    PKT_SIZE = 1024

    if DEBUG_TELEMETRY: print("[MSG]> start_telemetry_client()")
    if (RUN_TELEMETRY_THREAD == False): sys.quit()

    TEL_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TEL_socket.bind(('0.0.0.0',client_port))
    total_bytes_recv = 0

    try:
        while RUN_TELEMETRY_THREAD:
            telemetry_data = TEL_socket.recv(PKT_SIZE)
            telemetry_data = telemetry_data.decode()
            if not telemetry_data:
                if DEBUG_TELEMETRY: print('[MSG]> error: connection closed')
                break
            if DEBUG_TELEMETRY: print(telemetry_data)
            d=telemetry_data.split(',')
            if(d[0] == '$MOT'):
                if d[1]:
                    mot_data="Motor: {}".format(d[1])
                    func_success_msg(motor_log,mot_data)

    except Exception as e:
        if DEBUG_TELEMETRY: print("[MSG]> exception: {}".format(str(e)))
    finally:
        TEL_socket.close()
        if DEBUG_TELEMETRY: print("[MSG]> telemetry channel closed")
        func_error_msg(tag_log,"Telemetry stopped")

# ##############################################################################
#
# System functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# func_system_cmd(robot_ip,robot_port,msg_string)
# ------------------------------------------------------------------------------
def func_system_cmd(robot_ip,robot_port,msg_string):
    PKT_SIZE = 1024
    global DEBUG_SYSTEM
    try:
        client_socket = socket.socket()
        client_socket.connect((robot_ip,robot_port))
        if DEBUG_SYSTEM: print("[MSG]> success: connected to {}:{}".format(robot_ip,robot_port))
    except Exception as e:
        if DEBUG_SYSTEM: print("[MSG]> error: {}".format(str(e)))
        if DEBUG_SYSTEM: print("[MSG]> error: not connected to {}:{}".format(robot_ip,robot_port))
    try:
        client_socket.sendall(msg_string.encode())
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

# ------------------------------------------------------------------------------
# func_ping_rover()
# ------------------------------------------------------------------------------
def func_ping_rover():
    global ROVER_IP
    global system_log
    ret = func_icmp_echo_request(ROVER_IP)
    if(ret == 1):
        func_success_msg(system_log,'System: rover is UP')
        return True
    else:
        func_error_msg(system_log,'System: rover is DOWN')
        return False

# ------------------------------------------------------------------------------
# func_shutdown_btn()
# ------------------------------------------------------------------------------
def func_shutdown_btn():
    global system_log
    func_system_cmd(ROVER_IP,ROVER_SYSTEM_PORT,"sudo shutdown -h now")
    if GUI_SHOW_SYSTEM: func_error_msg(system_log,'System: shutdown Rover')
    if GUI_SHOW_CONTROL: stop_control_thread()
    if GUI_SHOW_VIDEO: stop_video_thread()

# ------------------------------------------------------------------------------
# func_reboot_btn()
# ------------------------------------------------------------------------------
def func_reboot_btn():
    global system_log
    func_system_cmd(ROVER_IP,ROVER_SYSTEM_PORT,"sudo shutdown -r now")
    if GUI_SHOW_SYSTEM: func_error_msg(system_log,'System: reboot Rover')
    if GUI_SHOW_CONTROL: stop_control_thread()
    if GUI_SHOW_VIDEO: stop_video_thread()

# ------------------------------------------------------------------------------
# func_icmp_echo_request(ip)
# ------------------------------------------------------------------------------
def func_icmp_echo_request(ip):
    icmp_delay = 2
    try:
        ret = subprocess.call("ping -c 1 -W {} {}".format(icmp_delay,ip), shell=True)
        if DEBUG_SYSTEM: print(ret)
    except:
        return -1
    if (ret == 0): return 1
    else: return -1

# ##############################################################################
#
# GUI functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# func_success_msg(log_box,msg)
# ------------------------------------------------------------------------------
def func_success_msg(log_box,msg):
    log_box['state'] = 'normal'
    log_box.delete(1.0, 2.0)
    log_box.insert('end',msg)
    log_box['bg'] = 'green'
    log_box['fg'] = 'white'
    log_box['state'] = 'disabled'

# ------------------------------------------------------------------------------
# func_error_msg(log_box,msg)
# ------------------------------------------------------------------------------
def func_error_msg(log_box,msg):
    log_box['state'] = 'normal'
    log_box.delete(1.0, 2.0)
    log_box.insert('end',msg)
    log_box['bg'] = 'red'
    log_box['fg'] = 'white'
    log_box['state'] = 'disabled'

# ##############################################################################
#
# Misc functions
#
# ##############################################################################

# ------------------------------------------------------------------------------
# func_get_setting(setting)
# ------------------------------------------------------------------------------
def func_get_setting(setting):
    f = open(ROVER_CONFIG_FILE, 'r')
    x = f.readlines()
    f.close()
    for item in x:
        item=item.rstrip("\r\n").replace(" ","")
        s,v=item.split("=")
        if(s == setting):return v
    return False

# ------------------------------------------------------------------------------
# func_exit_btn()
# ------------------------------------------------------------------------------
def func_exit_btn():
    global tk_win
    global player_pid

    global RUN_CONTROL_THREAD
    global RUN_VIDEO_THREAD
    global RUN_TELEMETRY_THREAD
    global RUN_SUPERVISOR_THREAD

    if DEBUG_SYSTEM: print("[MSG]> exit_btn()")

    RUN_CONTROL_THREAD = False
    RUN_VIDEO_THREAD = False
    RUN_TELEMETRY_THREAD = False
    RUN_SUPERVISOR_THREAD = False

    try:
        if psutil.pid_exists(player_pid):
            if DEBUG_OUTPUT: print("[MSG]> kill video player - pid: {}".format(player_pid))
            p = psutil.Process(int(player_pid))
            p.kill()
            player_pid = None

    finally:
        if DEBUG_OUTPUT: print("[MSG]> quit tk window")
        tk_win.destroy()

        if DEBUG_OUTPUT: print("[MSG]> exit program")
        os.system("kill {}".format(os.getpid()))
        sys.exit()

# ##############################################################################
#
# Main
#
# ##############################################################################

if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # Check if an instance of the program is already running.
    # --------------------------------------------------------------------------
    try:
        me = singleton.SingleInstance()
    except:
        if DEBUG_OUTPUT: print("[MSG]> error: program is already running")
        sys.exit()

    # --------------------------------------------------------------------------
    # Get configuration values from file
    # --------------------------------------------------------------------------
    try:
        ROVER_IP = func_get_setting('ROVER_IP')
        ROVER_SYSTEM_PORT = int(func_get_setting('ROVER_SYSTEM_PORT'))
        ROVER_CONTROL_PORT = int(func_get_setting('ROVER_CONTROL_PORT'))
        ROVER_VIDEO_PORT = int(func_get_setting('ROVER_VIDEO_PORT'))
        ROVER_TELEMETRY_PORT = int(func_get_setting('ROVER_TELEMETRY_PORT'))
        CLIENT_TELEMETRY_PORT = int(func_get_setting('CLIENT_TELEMETRY_PORT'))
        GUI_SHOW_SYSTEM = int(func_get_setting('GUI_SHOW_SYSTEM'))
        GUI_SHOW_CONTROL = int(func_get_setting('GUI_SHOW_CONTROL'))
        GUI_SHOW_VIDEO = int(func_get_setting('GUI_SHOW_VIDEO'))

        if DEBUG_OUTPUT: print("ROVER_IP: {}".format(ROVER_IP))
        if DEBUG_OUTPUT: print("ROVER_CONTROL_PORT: {}".format(ROVER_CONTROL_PORT))
        if DEBUG_OUTPUT: print("ROVER_VIDEO_PORT: {}".format(ROVER_VIDEO_PORT))
        if DEBUG_OUTPUT: print("ROVER_TELEMETRY_PORT: {}".format(ROVER_TELEMETRY_PORT))
        if DEBUG_OUTPUT: print("CLIENT_TELEMETRY_PORT: {}".format(CLIENT_TELEMETRY_PORT))
        if DEBUG_OUTPUT: print("ROVER_SYSTEM_PORT: {}".format(ROVER_SYSTEM_PORT))
        if DEBUG_OUTPUT: print("GUI_SHOW_CONTROL: {}".format(GUI_SHOW_CONTROL))
        if DEBUG_OUTPUT: print("GUI_SHOW_VIDEO: {}".format(GUI_SHOW_VIDEO))
        if DEBUG_OUTPUT: print("GUI_SHOW_SYSTEM: {}".format(GUI_SHOW_SYSTEM))

    except Exception as e:
        if DEBUG_OUTPUT: print("[MSG]> error: configuration file rover.conf")
        if DEBUG_OUTPUT: print(str(e))
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Start supervision thread
    # --------------------------------------------------------------------------
    start_supervisor_thread()

    # --------------------------------------------------------------------------
    # Define Tk user interface
    # --------------------------------------------------------------------------
    geometry_string = "{}x{}+{}+{}".format(screen_width,screen_height,screen_x,screen_y)
    if DEBUG_SYSTEM: print("[MSG]> geometry: {}".format(geometry_string))
    
    # Create GUI object
    tk_win = Tk()
    tk_win.title("Rover Control")
    tk_win.geometry(geometry_string)
    
    # Define GUI layout
    start_btn = Button(tk_win, text="Start", command=start_all_treads)
    start_btn.pack(fill=BOTH, expand=1)
    stop_btn = Button(tk_win, text="Stop", command=stop_all_treads)
    stop_btn.pack(fill=BOTH, expand=1)
    
    if GUI_SHOW_SYSTEM:
        #system buttons
        ping_rover_btn = Button(tk_win, text="Ping Rover", command=func_ping_rover)
        ping_rover_btn.pack(fill=BOTH, expand=1)
        reboot_rover_btn = Button(tk_win, text="Reboot Rover", command=func_reboot_btn)
        reboot_rover_btn.pack(fill=BOTH, expand=1)
        shutdown_rover_btn = Button(tk_win, text="Shutdown Rover", command=func_shutdown_btn)
        shutdown_rover_btn.pack(fill=BOTH, expand=1)
        #system log box
        system_log = Text(tk_win, state='normal', width=20, height=1, wrap='none',font=('TkDefaultFont', font_size))
        system_log.pack(fill=BOTH)
        system_log['bg'] = 'red'
        system_log['fg'] = 'white'
        system_log.insert('end','System: no data')
        system_log['state'] = 'disabled'
        
    if GUI_SHOW_CONTROL:
        # control buttons
        start_control_btn = Button(tk_win, text="Start control", command=start_control_thread)
        start_control_btn.pack(fill=BOTH, expand=1)
        stop_control_btn = Button(tk_win, text="Stop control", command=stop_control_thread)
        stop_control_btn.pack(fill=BOTH, expand=1)
        # control log box
        control_log = Text(tk_win, state='normal', width=20, height=1, wrap='none',font=('TkDefaultFont', font_size))
        control_log.pack(fill=BOTH)
        control_log['bg'] = 'red'
        control_log['fg'] = 'white'
        control_log.insert('end','Control: no data')
        control_log['state'] = 'disabled'
        # motor log box
        motor_log = Text(tk_win, state='normal', width=20, height=1, wrap='none',font=('TkDefaultFont', font_size))
        motor_log.pack(fill=BOTH)
        motor_log['bg'] = 'red'
        motor_log['fg'] = 'white'
        motor_log.insert('end','Motor: no data')
        motor_log['state'] = 'disabled'

    if GUI_SHOW_VIDEO:
        # video buttons
        start_video_btn = Button(tk_win, text="Start video", command=start_video_thread)
        start_video_btn.pack(fill=BOTH, expand=1)
        stop_video_btn = Button(tk_win, text="Stop video", command=stop_video_thread)
        stop_video_btn.pack(fill=BOTH, expand=1)
        # video log box
        video_log = Text(tk_win, state='normal', width=20, height=1, wrap='none',font=('TkDefaultFont', font_size))
        video_log.pack(fill=BOTH)
        video_log['bg'] = 'red'
        video_log['fg'] = 'white'
        video_log.insert('end','Video: no data')
        video_log['state'] = 'disabled'

    exit_btn = Button(tk_win, text="Exit", command=func_exit_btn)
    exit_btn.pack(fill=BOTH, expand=1)

    # --------------------------------------------------------------------------
    # Start Tk main activity
    # --------------------------------------------------------------------------
    tk_win.mainloop()
