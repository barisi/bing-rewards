import sys
import os
from src.driver import Rewards
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import pytz
from logging import basicConfig, DEBUG, debug, exception
import time


DRIVERS_DIR             = "drivers"
DRIVER                  = "chromedriver"

LOG_DIR                 = "logs"
ERROR_LOG               = "error.log"
HIST_LOG                = "hist.log"

DEBUG                   = True
HEADLESS                = True



class HistLog:
    __DATETIME_FORMAT   = "%A, %B %d %Y %I:%M%p %Z"

    __LOCAL_TIMEZONE    = tzlocal()
    __PST_TIMEZONE      = pytz.timezone("US/Pacific")

    __RESET_HOUR        = 0 # AM PST
    __MAX_HIST_LEN      = 7 # days

    __COMPLETED_TRUE    = "Successful"
    __COMPLETED_FALSE   = "Failed"


    def __init__(self, path, run_datetime=datetime.now()):
        self.path = path
        self.run_datetime = run_datetime.replace(tzinfo=self.__LOCAL_TIMEZONE)
        self.hist = self.__read()

    def __read(self):
        if not os.path.exists(self.path):
            return []
        else:
            with open(self.path, "r") as log:
                return [line.strip("\n") for line in log.readlines()]

    def get_timestamp(self):
        return self.run_datetime.strftime(self.__DATETIME_FORMAT)
    def not_run_today(self):
        # check if already ran today
        ran = False
        if len(self.hist) > 0:
            last_ran, completed = self.hist[-1].split(": ")

            last_ran_pst = datetime.strptime(last_ran, self.__DATETIME_FORMAT).replace(tzinfo=self.__LOCAL_TIMEZONE).astimezone(self.__PST_TIMEZONE)
            run_datetime_pst = self.run_datetime.astimezone(self.__PST_TIMEZONE)
            days_passed = (run_datetime_pst.date()-last_ran_pst.date()).days
            if ((days_passed == 0 and last_ran_pst.hour >= self.__RESET_HOUR) or 
                (days_passed == 1 and run_datetime_pst.hour < self.__RESET_HOUR)):
                if completed == self.__COMPLETED_TRUE:
                    ran = True
                else:
                    self.hist.pop()
    
        if not ran:
            # update hist with todays time stamp
            self.hist.append(self.get_timestamp())
            if len(self.hist) == self.__MAX_HIST_LEN:
                self.hist = self.hist[1:]
            return True
        else:
            return False
    def write(self, completed):
        self.hist[-1] = "{}: {}".format(self.hist[-1], self.__COMPLETED_TRUE if completed else self.__COMPLETED_FALSE)
        with open(self.path, "w") as log:
            log.write("\n".join(self.hist) + "\n")


def change_to_top_dir(arg0):
    dir_run_from = os.getcwd()
    top_dir = os.path.dirname(arg0)
    if top_dir and top_dir != dir_run_from:
        os.chdir(top_dir)
def get_formatted_time(time_elapsed):
    seconds = time_elapsed.seconds
    minutes = seconds//60
    seconds = seconds%60
    formatted_time = "{0}:{1:>02d}:{2:>03d}".format(minutes, seconds, time_elapsed.microseconds//1000)
    print("Elapsed time: {}".format(formatted_time))
    return formatted_time
    



if __name__ == "__main__":
    ## daily mode
    ## python BingRewards.py -d
    if len(sys.argv) == 2:
        assert sys.argv[1] == "-d"

        change_to_top_dir(sys.argv[0])
        
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        hist_log = HistLog(os.path.join(LOG_DIR, HIST_LOG))

        # get credentials
        try:
            from src import config
        except: # missing config file
            basicConfig(level=DEBUG, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))
            exception(hist_log.get_timestamp())
            debug("")
            quit()

        if not os.path.exists(DRIVERS_DIR):
            os.mkdir(DRIVERS_DIR)
        rewards = Rewards(os.path.join(DRIVERS_DIR, DRIVER), config.credentials["email"], config.credentials["password"], DEBUG, HEADLESS)


        if hist_log.not_run_today():
            try:
                completed = rewards.complete_all()
            except:
                basicConfig(level=DEBUG, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))
                exception(hist_log.get_timestamp())
                debug("")
                quit()

            hist_log.write(completed)

        else:
            print("Already ran script")


    ## interactive mode
    ## python BingRewards.py
    else:
        change_to_top_dir(sys.argv[0])

        input_message = "Enter \t{}, \n\t{}, \n\t{}, \n\t{}, \n\t{} \nInput: \t".format("w for web", "m for mobile", "b for both", "o for offers", "a for all (default)")
        try:
            arg = raw_input(input_message) # python 2
        except:
            arg = input(input_message) # python 3

        # get credentials
        try:
            from src import config
        except:
            print("\n{}".format("Failed to import configuration file"))
            time.sleep(1)
            raise
        
        if not os.path.exists(DRIVERS_DIR):
            os.mkdir(DRIVERS_DIR)
        rewards = Rewards(os.path.join(DRIVERS_DIR, DRIVER), config.credentials["email"], config.credentials["password"], DEBUG, HEADLESS)
    

        arg = arg.lower()
        if arg == "w":
            print("\n\t{}\n".format("You selected web"))
            rewards.complete_web_search()
        elif arg == "m":
            print("\n\t{}\n".format("You selected mobile"))
            rewards.complete_mobile_search()
        elif arg == "b":
            print("\n\t{}\n".format("You selected both web and mobile"))
            rewards.complete_both()
        elif arg == "o":
            print("\n\t{}\n".format("You selected offers"))
            rewards.complete_offers()
        else:
            print("\n\t{}\n".format("You selected all"))
            completed = rewards.complete_all()

            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            hist_log = HistLog(os.path.join(LOG_DIR, HIST_LOG))
            if hist_log.not_run_today():
                hist_log.write(completed)

