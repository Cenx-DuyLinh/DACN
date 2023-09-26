from pymavlink import mavutil
import time
from enum import Enum
import numpy as np
from .Log import GPSLogger
import threading

class ProgressStatus(Enum):
    OK = 0
    ERROR = 1

class MyMAVlink():
    def __init__(self, connection_string, baudrate, queue):
        self.queue = queue
        self.AI_data = None
        self.AI_control_parameters = None
        self.set_frame_msg_sent = False
        self.ai_auto_control_stop_flag = True
        # self.GPS_logger = GPSLogger()
        # self.mannequin_GPS = self.GPS_logger.read_GPS()
        # if self.mannequin_GPS:
        #     self.current_altitude = self.mannequin_GPS[2]
        # else:
        #     self.current_altitude = None
        # self.takeoff_point_GPS = [129724600, 1014566935, 0] #old home
        # #self.takeoff_point_GPS = [129727122, 1014567286, 0]
        # self.transit_point_GPS = [129704180, 1014561580, 0]
        # self.camera_resolution = [640, 480]
        # self.camera_FOV = [107, 93] #image crop from [1280, 720][122, 93 deg] to [640, 480][107, 93 deg]
        self.connection = mavutil.mavlink_connection(connection_string, baud = baudrate)
        self.boot_time = time.time()
        self.connection_status = self.wait_for_connection(10)
        if self.connection_status == ProgressStatus.OK:
            self.target_system = self.connection.target_system
            self.target_component = self.connection.target_component
        elif self.connection_status == ProgressStatus.ERROR:
            raise ConnectionError("Invalid MAVlink connection")
        
    def wait_for_connection(self, wait_timeout) -> ProgressStatus:
        """
        Sends a ping to stabilish the UDP communication and awaits for a response
        """
        msg = None
        wait_time = 0
        while not msg:
            self.connection.mav.ping_send(
                int(time.time() * 1e6), # Unix time in microseconds
                0,# Ping number
                0,# Request ping of all systems
                0 # Request ping of all components
                )
            msg = self.connection.recv_match()
            wait_time += 1
            if wait_time == wait_timeout:
                break
            time.sleep(1)
    
        if msg != None:
            return ProgressStatus.OK
        else: 
            return ProgressStatus.ERROR
    
    def command_acknowledge(self):
        time_out = 20
        timer = 0
        msg_CMDACK = None
        
        while not msg_CMDACK:
            msg_CMDACK = self.connection.recv_match(type = "COMMAND_ACK", blocking = False)
            if msg_CMDACK:
                msg_name = mavutil.mavlink.enums['MAV_CMD'][msg_CMDACK.command].name
                msg_result = mavutil.mavlink.enums['MAV_RESULT'][msg_CMDACK.result].name
                print(f"Got message: {msg_CMDACK.get_type()}")
                print(f"    Command ID: {msg_name}")
                print(f"    Command Result: {msg_result}")
                return f'{msg_name}\n   {msg_result}'
            time.sleep(0.1) 
            timer += 1
            if timer >= time_out:
                print("Time out. No Command Acknowledge recieved")
                return f'No CMD_ACK received'
            
    def arm_disarm(self, data):
        #data = 0 DISARM
        #data = 1 ARM
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            data, 0, 0, 0, 0, 0, 0
        )
        
    def take_off(self, data):
        altitude = data
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,0,0,altitude
        )
    
    def return_to_land(self):
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0,
            0,0,0,0,0,0,0
        )
    
    def land(self):
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_MAV_LAND,
            0, 0, 0, 0, 0, 0, 0
        )
    
    def set_mode(self, mode):
        """_summary_

        Args:
            mode (_int_):   3 == auto
            
                            4 == guided
                            
                            5 == loiter
                            
                            6 == RTL
                            
                            9 == land
        """
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            1, mode,
            0, 0, 0, 0, 0
        )
        
    def set_home(self, data):
        mav_frame = 6
        latitude, longitude, altitude = data
        self.connection.mav.command_int_send(
            self.target_system,
            self.target_component,
            mav_frame,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME,
            0,
            0,
            0, 
            0, 
            0, 
            0,
            latitude,
            longitude,
            altitude
        )
    
    def set_frame_position(self, data):
        self.set_frame_msg_sent = False
        #Copter:
            #Use Position : 0b110111111000 / 0x0DF8 / 3576 (decimal)
            #Use Position and Yaw: 0b000111111000 / 0x01F8 / 504 (decimal)
        #type_mask = 3576
        
        type_mask = 504
        x, y, z = data
        self.connection.mav.set_position_target_local_ned_send(
            int(1e3 * (time.time() - self.boot_time)),          #time_boot_ms
            self.target_system,
            self.target_component,       #target_system, taget_component
            9, #frame valid options are: MAV_FRAME_LOCAL_NED = 1, MAV_FRAME_LOCAL_OFFSET_NED = 7, MAV_FRAME_BODY_NED = 8, MAV_FRAME_BODY_OFFSET_NED = 9
            type_mask,       #type_mask (only position)
            x, y, z,    #x, y, z positions in m
            0, 0, 0,    #vy, vy, vz velocity in m/s
            0, 0, 0,    #ax, ay, az acceleration
            0, 0        #yaw, yaw_rate
        )
        # time.sleep(0.5)
        # msg_position_control = None
        # time_out = 20
        # timer = 0
        # while not msg_position_control:
        #     self.connection.mav.command_long_send(
        #         self.target_system,
        #         self.target_component,
        #         mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
        #         0,
        #         85,
        #         0, 0, 0, 0, 0, 0
        #     )
        #     time.sleep(0.1)
        #     msg_position_control = self.connection.recv_match(type = "POSITION_TARGET_LOCAL_NED", blocking = False)
        #     if msg_position_control:
        #         print(msg_position_control)
        #         print("POSITION_TARGET_LOCAL_NED recieved")
        #         self.set_frame_msg_sent = True
        #     timer += 1
        #     if timer >= time_out:
        #         print("Time out. No POSITION_TARGET_LOCAL_NED recieved")
        #         break
            
    def do_change_yaw(self, data):
        """

        Args:
            data (_list_): [yaw angle, direction]
            #1: clockwise, -1: counterclockwise
        """
        
        yaw_angle, direction = data
        if yaw_angle < 0:
            yaw_angle = 0
        elif yaw_angle > 180:
            yaw_angle = 180 

        yaw_rate = yaw_angle / 4
        
        if yaw_rate <= 5:
            yaw_rate = 5
        elif yaw_rate >= 25:
            yaw_rate = 25
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,
            yaw_angle,  #deg
            yaw_rate,   #deg/s
            direction,  #1: clockwise, -1: counterclockwise
            1,          #relative offset
            0, 0, 0
        )
        
    def do_reposition(self, data):
        if data:
            mavframe = 6
            latitude, longitude, altitude = data
            
            self.connection.mav.command_int_send(
                self.target_system,
                self.target_component,
                mavframe,
                mavutil.mavlink.MAV_CMD_DO_REPOSITION,
                0, 0,
                -1, 1,
                0, 0,
                latitude, longitude, altitude
            )
        else:
            print("    Empty GPS Data")
            
    def set_speed(self, data):
        """_summary_

        Args:
            data (_type_): [speedtype:(0=Airspeed, 1=Ground Speed, 2=Climb Speed, 3=Descent Speed), speed (m/s)]
        """
        speedtype, speed = data
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0,
            speedtype,
            speed,
            -1,0,0,0,0
        )
    
    def mission_interaction(self, data):
        """_summary_

        Args:
            data (_int_): : 0: Pause current mission or reposition command, hold current position. 1: Continue mission. 
        """
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_DO_PAUSE_CONTINUE,
            0,
            data,
            0, 0, 0, 0, 0, 0
        )

    def set_current_mission(self, mission_id):
        self.connection.mav.command_long_send(
            self.target_system,
            self.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MISSION_CURRENT,
            0,
            mission_id,
            1, #reset mission true = 1, false = 0
            0, 0, 0, 0, 0
        )
        
    def rc_channel_override(self, data):
        channels, pwms = data
        rc_channel_value = [65535 for _ in range(8)]
        for i in range(len(channels)):
                rc_channel_value[channels[i] - 1] = pwms[i]
        self.connection.mav.rc_channels_override_send(
            self.target_system,
            self.target_component,
            *rc_channel_value
        )
        
    def get_gps_position(self):
        #GPS
        #Version: Surely get newest GPS position
        time_out = 20
        timer = 0
        msg_GPS = None
        
        while not msg_GPS:
            self.connection.mav.command_long_send(
                self.target_system,
                self.target_component,
                mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
                0,
                33,
                0, 0, 0, 0, 0, 0
            )
            time.sleep(0.1)
            msg_GPS = self.connection.recv_match(type = "GLOBAL_POSITION_INT", blocking = False)
            if msg_GPS:
                print(f"Got message: {msg_GPS.get_type()}")
                print(f"    Timeboot (s): {msg_GPS.time_boot_ms/1e3}")
                print(f"    Latitude, Longitude: {msg_GPS.lat/1e7, msg_GPS.lon/1e7}")
                print(f"    Altitude ASL, Altitude AH: {msg_GPS.alt/1e3, msg_GPS.relative_alt/1e3}")
                self.current_altitude = round(float(msg_GPS.relative_alt/1e3))
                self.mannequin_GPS = [int(msg_GPS.lat), int(msg_GPS.lon), self.current_altitude]
                self.GPS_logger.save_GPS(self.mannequin_GPS)
                break 
            timer += 1
            if timer >= time_out:
                print("    Time out. No GPS recieved")
                break
            
    def move_forward(self, distance):
        self.set_frame_position([distance, 0, 0])
    
    def move_backward(self, distance):
        self.set_frame_position([-distance, 0, 0])
    
    def move_left(self, distance):
        self.set_frame_position([0, -distance, 0])
        
    def move_right(self, distance):
        self.set_frame_position([0, distance, 0])
        
    def move_up(self, distance):
        self.set_frame_position([0, 0, -distance])
        
    def move_down(self, distance):
        self.set_frame_position([0, 0, distance])
    
    def remove_outliers_and_average(self, data):
        u = np.mean(data)
        s = np.std(data)
        filtered = [e for e in data if ((u-2*s)<e<(u+2*s))]
        avg = round(np.average(filtered),2)
        return avg
    
    def get_ai_target_data(self):
        if not self.current_altitude:
            self.current_altitude = 40
            
        try:
            X_parameters = []
            Y_parameters = []
            
            while not self.queue.empty():
                x_ai, y_ai = self.queue.get_nowait()
                X_parameters.append(x_ai)
                Y_parameters.append(y_ai)
                
            X_AI = self.remove_outliers_and_average(X_parameters[-10:])
            Y_AI = self.remove_outliers_and_average(Y_parameters[-10:])
            self.AI_data = [X_AI, Y_AI]
            print("    AI_data: ", self.AI_data)
            
        except Exception as e:
            print(e)
            self.AI_data = None
            print("    Can't calculate AI Data")
            
        if self.AI_data:
            x, y = self.AI_data
            H_distance = round(x * np.tan(np.deg2rad(self.camera_FOV[0]/2)) * self.current_altitude, 1)
            V_distance = round(y * np.tan(np.deg2rad(self.camera_FOV[1]/2)) * self.current_altitude, 1)
            self.AI_control_parameters = [V_distance, H_distance, 0]
            #print("    Control parameters: ", self.AI_control_parameters)
        else:
            self.AI_control_parameters = None
            print("    Can't calculate AI control parameters")
        
    def ai_control(self):
        if self.AI_control_parameters:
            self.set_frame_position(self.AI_control_parameters)
        else:
            print("    Can't set AI control parameters")
    
    def ai_stop_autocontrol(self):
        self.ai_auto_control_stop_flag = True
        print(f"AI AUTO CONTROL STOP")
    
    def ai_start_autocontrol(self):
        print(f"AI AUTO CONTROL START")
        if self.ai_auto_control_stop_flag:
            self.ai_auto_control_stop_flag = False
            thread = threading.Thread(target=self.ai_auto_control_thread)
            thread.start()
        
    def ai_auto_control_thread(self):
        while True:
            try:
                if self.ai_auto_control_stop_flag:
                    break
                
                #Get AI control parameters
                self.get_ai_target_data()

                #Limit the control parameters
                for i in range(3):
                    if self.AI_control_parameters[i] < -10:
                        self.AI_control_parameters[i] = -10
                    elif self.AI_control_parameters[i] > 10:
                        self.AI_control_parameters[i] = 10
                
                #Send the AI control parameters
                print("    Control parameters: ", self.AI_control_parameters)
                self.ai_control()
                
                #Check the distance to move
                distance_to_move = round(np.sqrt(self.AI_control_parameters[0]**2 + self.AI_control_parameters[1]**2), 1)
                print("    Distance to Move: ", distance_to_move)
                
                #Delay until finish
                time.sleep(distance_to_move)
                time.sleep(2)
                
                #Drop the package
                if distance_to_move <= 3:
                    time.sleep(2)
                    print("GET GPS POSITION")
                    for i in range(3):
                        self.get_gps_position()
                    time.sleep(2)
                    print("DROP PACKAGE")
                    for i in range(3):
                        self.rc_channel_override([[6],[2000]])
                    self.ai_stop_autocontrol()
                    break

            except Exception as e:
                print(e)