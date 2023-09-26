import logging
import numpy as np

class GPSLogger():
    def __init__(self):
        self.logger= logging.getLogger('logger_GPS')
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler('DACN\CopterAAVC\Log\GPS.log')
        self.formatter = logging.Formatter(fmt ='%(asctime)s \n    %(message)s\n______________________________', datefmt= 'Date: %d/%m/%y Time: %H:%M:%S')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        
    def save_GPS(self, GPS_location):
        try:
            lat, lon, alt = GPS_location
            self.logger.info(f"Latitude: {lat}\n    Longitude: {lon}\n    Altitude: {alt}")
        except Exception as e:
            print(e)
        
    def read_GPS(self):
        GPS_position = []
        try:
            with open('CopterAAVC/Log/GPS.log', 'r') as f:
                contents = f.read().split("______________________________")
                parts = contents[-2].strip().split("\n    ")
                print("Read GPS position on: ", parts[0])
                for i in parts[1:4]:
                    a = i.split(": ")[1]
                    GPS_position.append(int(a))
            print("    GPS position: ", GPS_position)
            return GPS_position
        except:
            print("No GPS position from log file!")
            return None