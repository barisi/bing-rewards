#!/usr/bin/env python3

import sys
import os
from src.rewards import Rewards
from src.log import HistLog
import logging


DRIVERS_DIR                = "drivers"
DRIVER                     = "chromedriver"

LOG_DIR                    = "logs"
ERROR_LOG                  = "error.log"
RUN_LOG                    = "run.log"
SEARCH_LOG                 = "search.log"

DEBUG                      = True
HEADLESS                   = False


## TODO
#
#  try getting quiz progress only in the beginning to check how many total searches are required instead of every time
#  



def __main(arg0, arg1):
    # change to top dir
    dir_run_from = os.getcwd()
    top_dir = os.path.dirname(arg0)
    if top_dir and top_dir != dir_run_from:
        os.chdir(top_dir)


    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    hist_log = HistLog(os.path.join(LOG_DIR, RUN_LOG), os.path.join(LOG_DIR, SEARCH_LOG), os.path.join(LOG_DIR, ERROR_LOG))

    # get credentials
    try:
        from src import config
    except:
        out = "Failed to import configuration file"
        print("\n{}".format(out))
        hist_log.log_exception([out])
        raise

    if not os.path.exists(DRIVERS_DIR):
        os.mkdir(DRIVERS_DIR)
    rewards = Rewards(os.path.join(DRIVERS_DIR, DRIVER), config.credentials["email"], config.credentials["password"], hist_log.get_search_hist(), DEBUG, HEADLESS)


    try:
        if arg1 in ["w", "web"]:
            print("\n\t{}\n".format("You selected web search"))
            rewards.complete_web_search()
            hist_log.log_completion(rewards.completion)
        elif arg1 in ["m", "mobile"]:
            print("\n\t{}\n".format("You selected mobile search"))
            rewards.complete_mobile_search()
            hist_log.log_completion(rewards.completion)
        elif arg1 in ["b", "both"]:
            print("\n\t{}\n".format("You selected both searches"))
            rewards.complete_both_searches()
            hist_log.log_completion(rewards.completion)
        elif arg1 in ["o", "other"]:
            print("\n\t{}\n".format("You selected offers"))
            rewards.complete_offers()
            hist_log.log_completion(rewards.completion)
        elif arg1 in ["a", "all"]:
            print("\n\t{}\n".format("You selected all"))
            rewards.complete_all()
            hist_log.log_completion(rewards.completion)
        else:
            print("\n\t{}\n".format("You selected remaining"))
            completion = hist_log.get_completion()
            if not completion.is_all_completed():
                if not completion.is_any_completed():
                    rewards.complete_all()
                elif not completion.is_any_searches_completed():
                    rewards.complete_both_searches()
                elif not completion.is_web_search_completed() and not completion.is_offers_completed():
                    rewards.complete_web_search_and_offers()
                elif not completion.is_mobile_search_completed() and not completion.is_offers_completed():
                    rewards.complete_mobile_search(print_stats=False)
                    rewards.complete_offers()
                elif not completion.is_offers_completed():
                    rewards.complete_offers()
                elif not completion.is_mobile_search_completed():
                    rewards.complete_mobile_search()
                else:
                    rewards.complete_web_search()

                hist_log.log_completion(rewards.completion)
                completion = hist_log.get_completion()
                if not completion.is_all_completed(): # check again, log if any failed
                    hist_log.log_warning(rewards.stdout)

            else:
                print("Nothing to do")

    except:
        hist_log.log_completion(rewards.completion)
        hist_log.log_exception(rewards.stdout)
        raise
    

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        out = "Enter \t{}, \n\t{}, \n\t{}, \n\t{}, \n\t{}, \n\t{} \nInput: \t"
        input_message = out.format("w for web", "m for mobile", "b for both", "o for offers", "a for all","r for remaining (default)")
        try:
            arg1 = raw_input(input_message) # python 2
        except:
            arg1 = input(input_message) # python 3
        arg1 = arg1.lower()

        __main(args[0], arg1)

    elif len(args) == 2:
        arg1 = args[1].lower()
        assert arg1 in ["-w", "--web", "-m", "--mobile", "-b", "--both", "-o", "--offers", "-a", "-all", "-r", "--remaining"]

        __main(args[0], arg1.replace("-", ""))

    else:
        print("Incorrect number of arguments")


