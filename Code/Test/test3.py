import logging
import time

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="testfolder/logfile", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    date = time.localtime()
    logging.info(f"--------------------------[New Run File]--[{date.tm_mday}/{date.tm_mon}/{date.tm_year}]--[{date.tm_hour}:{date.tm_min}]-----------------------------")
    for i in range(0, 10) :
        logging.info(f"hello{i}")
