import os
import platform
try:
    from urllib.request import urlopen
except ImportError: # python 2
    from urllib2 import urlopen
import zipfile
import getpass
import base64


WINDOWS_DRIVER_URL    = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_win32.zip"
MAC_DRIVER_URL        = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_mac64.zip"

DRIVERS_DIR           = "BingRewards/drivers/"
CONFIG_FILE_PATH      = "BingRewards/src/config.py"

CONFIG_FILE_TEMPLATE = """credentials = dict(
    email = '{0}',
    password = '{1}',
)
"""


def download_driver(url):
    response = urlopen(url)
    zip_file_path = os.path.join(DRIVERS_DIR, os.path.basename(WINDOWS_DRIVER_URL))
    with open(zip_file_path, 'wb') as zip_file:
        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            zip_file.write(chunk)

    extracted_dir = os.path.splitext(zip_file_path)[0]
    with zipfile.ZipFile(zip_file_path, "r") as zip_file:
        zip_file.extractall(extracted_dir)
    os.remove(zip_file_path)

    driver = os.listdir(extracted_dir)[0]
    os.rename(os.path.join(extracted_dir, driver), os.path.join(DRIVERS_DIR, driver))
    os.rmdir(extracted_dir)




## download chrome driver
if not os.path.exists(DRIVERS_DIR):
    os.mkdir(DRIVERS_DIR)

if len(os.listdir(DRIVERS_DIR)) == 0:
    print("Downloading drivers..")
    system = platform.system()
    if system == "Windows":
        download_driver(WINDOWS_DRIVER_URL)
    elif systemm == "Darwin":
        download_driver(MAC_DRIVER_URL)


## create config file
if not os.path.exists(CONFIG_FILE_PATH):
    print("Generating configuration file..")
    try:
        email = base64.b64encode(raw_input("     Email: ").encode()).decode()
    except:
        email = base64.b64encode(input("     Email: ").encode()).decode()
    print("    Hashed: {}\n".format(email))

    password = base64.b64encode(getpass.getpass("  Password: ").encode()).decode()
    print("    Hashed: {}\n".format(password))

    new_config = CONFIG_FILE_TEMPLATE.format(email, password)
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config_file.write(new_config)


