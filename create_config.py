import getpass
import os
import base64
import time


CONFIG_FILE_PATH     = "BingRewards/src/config.py"

CONFIG_FILE_TEMPLATE = """credentials = dict(
    email = '{0}',
    password = '{1}',
)
"""


# get hashed credentials 
#email = base64.b64encode(getpass.getpass("Enter email: ").encode()).decode()
try:
    email = base64.b64encode(raw_input("Enter email: ").encode()).decode()
except:
    email = base64.b64encode(input("Enter email: ").encode()).decode()
print("{}\n".format(email))
password = base64.b64encode(getpass.getpass("Enter password: ").encode()).decode()
print("{}\n".format(password))

new_config = CONFIG_FILE_TEMPLATE.format(email, password)

# check if config file exists
if not os.path.isfile(CONFIG_FILE_PATH):
    # create new config file
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config_file.write(new_config)
        print("Successfully created config file")
else:
    with open(CONFIG_FILE_PATH, "r") as config_file:
        cur_config = config_file.read()
    if new_config != cur_config:
        # rewrite config file
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config_file.writelines(new_config)
        print("Successfully updated config file")
    else:
        print("Config file already contains latest credentials")

time.sleep(2)
