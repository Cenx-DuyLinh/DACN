from pymavlink import mavutil
import time
from CopterAAVC.Class.MAVlink import MyMAVlink

# Connect to the Pixhawk
connection_string = '/dev/serial0'  # Replace with the correct serial port for your Pixhawk
baudrate = 921600  # Replace with the correct baudrate for your Pixhawk
con = MyMAVlink(connection_string=connection_string,baudrate=baudrate,queue=0)
master = con
print(con.connection_status)

# Print the system status

while True:
    master.connection.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        30,
        1e6,
        0,0,0,0,0
    )

    response_ATT = master.connection.recv_match(type='COMMAND_ACK', blocking = False)
    #print(response_ATT)
    if response_ATT:
        
        break
# Continuous monitoring of messages
while True:
    # Check if there is a new message available
    message = master.connection.recv_match(type = "ATTITUDE",blocking = False)

    #print(message)
    

    # ... Continue processing or add a delay if desired