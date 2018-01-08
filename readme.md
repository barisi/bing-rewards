# bing-rewards
An automated solution for earning daily Microsoft Rewards points. 


## Getting Started
1. This solution requires Google Chrome which can be downloaded from https://www.google.com/chrome/browser/desktop/index.html.
2. If you don't already have Python installed, visit https://www.python.org/. 
3. Now install the dependencies using the *__BingRewards/requirements.txt__* file included in the repo: `pip install -r BingRewards/requirements.txt`.
4. Next you'll need to create a configuration file that stores your Micrrosoft account credentials. Run *__create_config.py__* and enter the necessary info. This will create the file *__BingRewards/src/config.py__* for you. Rest assured, **your credentials will NOT be stored in plain text.**
5. And you're all set! You can now either run *__BingRewards/BingRewards.py__* and follow the on-screen instructions to get started or pass the argument `-d` to run it entirely through: `python BingRewards/BingRewards.py -d`. You can also execute one of the two, *__run_windows.vbs__* or *__run_mac.app__* depending on your OS, to run the script without any terminals or command lines popping up. This way, there is no interference with your daily routine.

## Scheduling (Optional)
You may want to use your operating system's scheduler to run the script every time you unlock your machine and/or everyday at 12AM PST incase you leave your machine running for periods longer than 24 hours.

### Windows
1. Open *Task Scheduler* and click *Create Task*.
2. Add a new trigger, either *On workstation unlock* for your specific username or *On a schedule* daily depending on what you want. 
3. When adding the action, you may need to point the program to *__C:/Windows/System32/wscript.exe__* and add *__/absolute/path/to/run_windows.vbs__* with the correct path as the argument. 
4. It's also recommended to add the condition to only execute when there is a network connection available.

### Mac

##### At Login
1. Navigate to *System Preferences > Users & Groups > Login Items* and add *__run_mac.app__*. Note, this will only get triggered after logging into your machine and not every time you unlock your computer.

##### At a Specific Time
1. For scheduling something daily, you can create a time-based job with cron. Open up the terminal and type: `crontab -e`. 
2. Now append the following line with the correct path: `0 0 * * * osascript /absolute/path/to/run_mac.app`. The second 0 is the hour (0-23) in your local timezone. Also note the default text editor for crontab is VIM so you'll need to hit `i` before inserting and finally `:wq` to write the changes and quit.

## Under the Hood
- Python 3.6
- ChromeDriver 2.34
- Selenium

## Disclaimer
- Results may vary if you are running a Mac. Most to all of the development was done on Windows.
- Storing passwords locally, even if they are hashed, should be handled with caution. **The user should avoid getting set up on a shared computer.** 
- Automation is a hobby and this project was a way to enhance my programming skills. As a result, it may also be seldomly maintained. 

## Known Issues
- Error retrieving current search progress.
- Engagement in daily offers suddenly hangs.
- Quiz offers failing to start.

These issues have been seen to be resolved running ChromeDriver outside of headless mode, however, at the time I have not provided a simple way to do this. Headless mode is a relatively new feature that allows Google Chrome to be launched in the background. Turning this feature off may interfere with the users daily routine. 

Some of these bug fixes may also be roled out in newer builds. You can download the latest release from https://sites.google.com/a/chromium.org/chromedriver/downloads and place the extracted file in *__BingRewards/drivers/__*.

## Future Work
- ~~Utilize Microsoft Edge's web driver to earn additional points.~~ (Solved with user agents!)
- Create a script to automate scheduling for the user.

