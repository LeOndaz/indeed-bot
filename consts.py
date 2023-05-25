import random
import re
from enum import Enum
from pathlib import Path

from fake_useragent import UserAgent as BaseUserAgent
from selenium.webdriver.common.by import By

DEBUG = True
PER_PAGE = 15
INDEED_URL = "https://eg.indeed.com/"
INDEED_LOGIN_URL = "https://eg.indeed.com/account/login"
WEB_DRIVER_PATH = Path("chromedriver").resolve()
STEPPER_PATTERN = re.compile("Application step [0-9]+ of (?P<count>[0-9]+)")

PROFILE_PATH = f"{Path(__file__).resolve().parent}/Profile"


class UserAgent(BaseUserAgent):
    def random(self):
        return random.choice([self.chrome, self.edge, self.firefox])


ua = UserAgent()

LOGIN_FORM_LOCATOR = (
    By.ID,
    "emailform",
)

EMAIL_INPUT_LOCATOR = (
    By.ID,
    "login-email-input",
)

PASSWORD_INPUT_LOCATOR = (
    By.ID,
    "login-password-input",
)

LOGIN_BTN_LOCATOR = (
    By.ID,
    "login-submit-button",
)

WHAT_WHERE_FORM_LOCATOR = (
    By.ID,
    "whatWhere",
)

WHAT_INPUT_LOCATOR = (
    By.ID,
    "text-input-what",
)

WHERE_INPUT_LOCATOR = (
    By.ID,
    "text-input-where",
)

FIND_BTN_LOCATOR = (
    By.TAG_NAME,
    "button",
)

FILTERS_INPUT_LOCATOR = (By.CLASS_NAME, "filters")


class DatePostedLocators(Enum):
    BTN_LOCATOR = (
        By.ID,
        "filter-dateposted",
    )

    LAST_24_HOURS = (By.XPATH, "//a[@title='Last 24 Hours']")

    LAST_3_DAYS = (By.XPATH, "//a[@title='Last 3 days']")

    LAST_7_DAYS = (
        By.XPATH,
        "//a[@title='Last 7 days']",
    )

    SINCE_YOUR_LAST_VISIT = None  # We don't keep state.


class WithinDistanceLocators(Enum):
    BTN_LOCATOR = (
        By.ID,
        "filter-distance",
    )

    EXACT_LOCATION_ONLY = (
        By.XPATH,
        "//a[@title='Exact location only']",
    )

    OF_5_MILES = (
        By.XPATH,
        "//a[@title='within 5 miles']",
    )

    OF_10_MILES = (
        By.XPATH,
        "//a[@title='within 10 miles']",
    )

    OF_15_MILES = (
        By.XPATH,
        "//a[@title='within 15 miles']",
    )

    OF_25_MILES = (
        By.XPATH,
        "//a[@title='within 25 miles']",
    )

    OF_50_MILES = (
        By.XPATH,
        "//a[@title='within 50 miles']",
    )

    OF_100_MILES = (
        By.XPATH,
        "//a[@title='within 100 miles']",
    )


CAPTCHA_MESSAGE_LOCATOR = (By.CLASS_NAME, "pass-ErrorMessage")

JOB_CARD_LOCATORS = (
    (
        By.XPATH,
        "//div[contains(@class, 'slider_container')]/..",  # ALL anchor implementation
    ),
    (
        By.XPATH,
        '//*[contains(concat(" ", normalize-space(@class), " "), " jobsearch-SerpJobCard ")]',
    ),
)

APPLY_BTN_LOCATOR = (
    By.ID,
    "indeedApplyButton",
)

RESUME_INPUT_LOCATOR = (
    By.CLASS_NAME,
    "ia-Resume",
)

CONTINUE_BTN_LOCATOR = (
    By.CLASS_NAME,
    "ia-continueButton",
)

STEPPER_LOCATOR = (
    By.CLASS_NAME,
    "ia-Navigation-steps",
)

PAGINATION_LIST_LOCATOR = (
    By.CLASS_NAME,
    "pagination-list",
)

TWO_FACTOR_FORM_LOCATOR = (By.ID, "two-factor-auth-form")

TWO_FACTOR_INPUT_LOCATOR = (
    By.ID,
    "verification_input",
)

CONTACT_FORM_FIRST_NAME_LOCATOR = (
    By.ID,
    "input-firstName",
)

CONTACT_FORM_LAST_NAME_LOCATOR = (
    By.ID,
    "input-lastName",
)

CONTACT_FORM_CITY_LOCATOR = (
    By.ID,
    "input-location",
)

DatePosted = DatePostedLocators
WithinDistance = WithinDistanceLocators
