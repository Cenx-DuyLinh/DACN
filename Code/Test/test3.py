import logging
import time
import os
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_file = os.path.join(current_dir,"logfile")
    logging.basicConfig(level=logging.DEBUG, filename=current_file, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    date = time.localtime()
    logging.info(f"--------------------------[New Run File]--[{date.tm_mday}/{date.tm_mon}/{date.tm_year}]--[{date.tm_hour}:{date.tm_min}]-----------------------------")
    for i in range(0, 10) :
        logging.info(f"hello{i}")
