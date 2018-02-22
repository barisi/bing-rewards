import sys
import os
from src.driver import Rewards, Completion
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import pytz
from logging import basicConfig, DEBUG, debug, exception


DRIVERS_DIR                = "drivers"
DRIVER                     = "chromedriver"

LOG_DIR                    = "logs"
ERROR_LOG                  = "error.log"
HIST_LOG                   = "hist.log"

DEBUG                      = True
HEADLESS                   = True



class HistLog:
    __DATETIME_FORMAT      = "%A, %B %d %Y %I:%M%p %Z"

    __LOCAL_TIMEZONE       = tzlocal()
    __PST_TIMEZONE         = pytz.timezone("US/Pacific")

    __RESET_HOUR           = 0  # AM PST
    __MAX_HIST_LEN         = 30 # days

    __COMPLETED_TRUE       = "Successful"
    __COMPLETED_FALSE      = "Failed {}"

    __WEB_SEARCH_OPTION    = "Web Search"
    __MOBILE_SEARCH_OPTION = "Mobile Search"
    __OFFERS_OPTION        = "Offers"


    def __init__(self, path, run_datetime=datetime.now()):
        self.path = path
        self.run_datetime = run_datetime.replace(tzinfo=self.__LOCAL_TIMEZONE)
        self.hist = self.__read()
        self.__completion = Completion()

    def __read(self):
        if not os.path.exists(self.path):
            return []
        else:
            with open(self.path, "r") as log:
                return [line.strip("\n") for line in log.readlines()]

    def get_timestamp(self):
        return self.run_datetime.strftime(self.__DATETIME_FORMAT)
    def get_completion(self):
        # check if already ran today
        if len(self.hist) > 0:
            last_ran, completed = self.hist[-1].split(": ")

            last_ran_pst = datetime.strptime(last_ran, self.__DATETIME_FORMAT).replace(tzinfo=self.__LOCAL_TIMEZONE).astimezone(self.__PST_TIMEZONE)
            run_datetime_pst = self.run_datetime.astimezone(self.__PST_TIMEZONE)
            delta_days = (run_datetime_pst.date()-last_ran_pst.date()).days
            if ((delta_days == 0 and last_ran_pst.hour >= self.__RESET_HOUR) or 
                (delta_days == 1 and run_datetime_pst.hour < self.__RESET_HOUR)):
                
                if completed == self.__COMPLETED_TRUE:
                    self.__completion.web_search = True
                    self.__completion.mobile_search = True
                    self.__completion.offers = True
                else:
                    #self.hist.pop()
                    if self.__WEB_SEARCH_OPTION not in completed:
                        self.__completion.web_search = True
                    if self.__MOBILE_SEARCH_OPTION not in completed:
                        self.__completion.mobile_search = True
                    if self.__OFFERS_OPTION not in completed:
                        self.__completion.offers = True

        if not self.__completion.is_all_completed():
            # update hist with todays time stamp
            self.hist.append(self.get_timestamp())
            if len(self.hist) == self.__MAX_HIST_LEN:
                self.hist = self.hist[1:]

        return self.__completion
    def write(self, completion):
        self.__completion.update(completion)
        if not self.__completion.is_all_completed():
            if not self.__completion.is_any_completed():
                failed = "{}, {} & {}".format(self.__WEB_SEARCH_OPTION, self.__MOBILE_SEARCH_OPTION, self.__OFFERS_OPTION)
            elif not self.__completion.is_offers_completed():
                failed = "{}".format(self.__OFFERS_OPTION)
            elif not self.__completion.is_any_searches_completed():
                failed = "{} & {}".format(self.__WEB_SEARCH_OPTION, self.__MOBILE_SEARCH_OPTION)
            elif not self.__completion.is_mobile_search_completed():
                failed = "{}".format(self.__MOBILE_SEARCH_OPTION)
            else:
                failed = "{}".format(self.__WEB_SEARCH_OPTION)
            msg = self.__COMPLETED_FALSE.format(failed) 
        else:
            msg = self.__COMPLETED_TRUE

        self.hist[-1] = "{}: {}".format(self.hist[-1], msg)
        with open(self.path, "w") as log:
            log.write("\n".join(self.hist) + "\n")


def __main(arg0, arg1):
    # change to top dir
    dir_run_from = os.getcwd()
    top_dir = os.path.dirname(arg0)
    if top_dir and top_dir != dir_run_from:
        os.chdir(top_dir)


    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    hist_log = HistLog(os.path.join(LOG_DIR, HIST_LOG))

    # get credentials
    try:
        from src import config
    except:
        print("\nFailed to import configuration file")
        basicConfig(level=DEBUG, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))
        exception(hist_log.get_timestamp())
        debug("")
        raise

    if not os.path.exists(DRIVERS_DIR):
        os.mkdir(DRIVERS_DIR)
    rewards = Rewards(os.path.join(DRIVERS_DIR, DRIVER), config.credentials["email"], config.credentials["password"], DEBUG, HEADLESS)


    if arg1 in ["w", "web"]:
        print("\n\t{}\n".format("You selected web search"))
        completion = rewards.complete_web_search()
        if not hist_log.get_completion().is_web_search_completed():
            hist_log.write(completion)
    elif arg1 in ["m", "mobile"]:
        print("\n\t{}\n".format("You selected mobile search"))
        completion = rewards.complete_mobile_search()
        if not hist_log.get_completion().is_mobile_search_completed():
            hist_log.write(completion)
    elif arg1 in ["b", "both"]:
        print("\n\t{}\n".format("You selected both searches"))
        completion = rewards.complete_both_searches()
        if not hist_log.get_completion().is_both_searches_completed():
            hist_log.write(completion)
    elif arg1 in ["o", "other"]:
        print("\n\t{}\n".format("You selected offers"))
        completion = rewards.complete_offers()
        if not hist_log.get_completion().is_offers_completed():
            hist_log.write(completion)
    elif arg1 in ["a", "all"]:
        print("\n\t{}\n".format("You selected all"))
        completion = rewards.complete_all()
        if not hist_log.get_completion().is_all_completed():
            hist_log.write(completion)
    else:
        print("\n\t{}\n".format("You selected remianing"))
        try:
            completion = hist_log.get_completion()
            if not completion.is_all_completed():
                if not completion.is_any_completed():
                    completion = rewards.complete_all()
                elif not completion.is_offers_completed():
                    completion = rewards.complete_offers()
                elif not completion.is_any_searches_completed():
                    completion = rewards.complete_both_searches()
                elif not completion.is_mobile_search_completed():
                    completion = rewards.complete_mobile_search()
                else:
                    completion = rewards.complete_web_search()
                hist_log.write(completion)

            else:
                print("Nothing to do")
        except:
            basicConfig(level=DEBUG, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))
            exception(hist_log.get_timestamp())
            debug("")
            raise
    


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        input_message = "Enter \t{}, \n\t{}, \n\t{}, \n\t{}, \n\t{}, \n\t{} \nInput: \t".format("w for web", 
                                                                                                "m for mobile", 
                                                                                                "b for both", 
                                                                                                "o for offers", 
                                                                                                "a for all",
                                                                                                "r for remaining (default)")
        try:
            arg1 = raw_input(input_message) # python 2
        except:
            arg1 = input(input_message) # python 3
        arg1 = arg1.lower()

        __main(args[0], arg1)

    elif len(args) == 2:
        arg1 = args[1].lower()
        assert arg1 in ["-w", "--web", "-m", "--mobile", "-b", "--both", "-o", "--offers", "-a", "-all", "-r", "--remaining", "-d"]

        __main(args[0], arg1.replace("-", ""))

    else:
        print("Incorrect number of arguments")


