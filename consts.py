import random
import re
from pathlib import Path

from fake_useragent import UserAgent as BaseUserAgent

DEBUG = True
PER_PAGE = 15
US_INDEED_URL = "https://indeed.com/"
US_INDEED_LOGIN_URL = "https://indeed.com/account/login"
EG_INDEED_URL = "https://eg.indeed.com/"
EG_INDEED_LOGIN_URL = "https://eg.indeed.com/account/login"
WEB_DRIVER_PATH = Path("chromedriver").resolve()
STEPPER_PATTERN = re.compile("Application step [0-9]+ of (?P<count>[0-9]+)")

PROFILE_PATH = f"{Path(__file__).resolve().parent}/Profile"


class UserAgent(BaseUserAgent):
    def random(self):
        return random.choice([self.chrome, self.edge, self.firefox])


ua = UserAgent()

