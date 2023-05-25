import argparse
import logging
import re
import time
from inspect import iscoroutinefunction
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from consts import (
    APPLY_BTN_LOCATOR,
    CONTACT_FORM_FIRST_NAME_LOCATOR,
    CONTACT_FORM_LAST_NAME_LOCATOR,
    CONTINUE_BTN_LOCATOR,
    EMAIL_INPUT_LOCATOR,
    FILTERS_INPUT_LOCATOR,
    INDEED_LOGIN_URL,
    JOB_CARD_LOCATORS,
    LOGIN_BTN_LOCATOR,
    LOGIN_FORM_LOCATOR,
    PASSWORD_INPUT_LOCATOR,
    STEPPER_LOCATOR,
    STEPPER_PATTERN,
    TWO_FACTOR_FORM_LOCATOR,
    TWO_FACTOR_INPUT_LOCATOR,
    WEB_DRIVER_PATH,
    WHAT_INPUT_LOCATOR,
    WHAT_WHERE_FORM_LOCATOR,
    WHERE_INPUT_LOCATOR,
    WithinDistance,
    ua,
)
from errors import MissingInfoError, MustApplyOnCompanySiteError, NoStepperFoundError

logger = logging.getLogger(__file__)
f_handler = logging.FileHandler("logs.log")
f_handler.setLevel(logging.INFO)
f_format = logging.Formatter("[%(levelname)s]: %(asctime)s %(message)s")
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


def setup_webdriver(proxy=None):
    """
    Init a new webdriver changing user-agent every time..
    :return:
    """
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # enable proxy-ing
    if proxy:
        host, port = proxy
        options.add_argument(f"--proxy-server={host}:{port}")

    # save profile data
    # options.add_argument(f"user-data-dir={PROFILE_PATH}")

    service = webdriver.chrome.service.Service(executable_path="chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def navigate_to_indeed_login_page(driver: webdriver.Chrome):
    driver.get(INDEED_LOGIN_URL)


def open_in_new_tab(driver: webdriver.Chrome, url: str):
    driver.execute_script(f"window.open('{url}', '_blank')")


def switch_to_tab(driver: webdriver.Chrome, handle):
    """
    Switches to an active tab.
    :param driver: Driver to act on.
    :param tab_num: Tab number, 0-indexed.
    :return: None
    """
    driver.switch_to.window(handle)


def clear_input(input):
    input.get_attribute("value")
    input.send_keys(Keys.CONTROL + "A" + Keys.DELETE)


def filters_manager(driver):
    filters_list = driver.find_element(*FILTERS_INPUT_LOCATOR)

    def filter_by(val_enum):
        filter_element = filters_list.find_element(*val_enum.BTN_LOCATOR.value)
        filter_element.find_element_by_tag_name("button").click()
        anchor = filter_element.find_element(*val_enum.value)
        anchor.click()

    return filter_by


def paginated_search_manager(driver: webdriver.Chrome, what, where):
    """
    1-Indexed.
    :param what:
    :param where:
    :param driver:
    :return:
    """

    def switch_to(page_num):
        parsed_url = list(urlparse(driver.current_url))
        qs = parse_qs(parsed_url[4])
        qs["start"] = (page_num - 1) * 10

        if qs.get("query", None) is not None:
            qs["q"] = what

        if qs.get("location", None) is not None:
            qs["l"] = where

        new_qs = {
            key: val[0] if isinstance(val, list) else val for key, val in qs.items()
        }
        new_qs = urlencode(new_qs)
        parsed_url[4] = new_qs
        new_url = urlunparse(parsed_url)

        return driver.get(new_url)

    return switch_to


def next_step(driver):
    wait = WebDriverWait(driver, 5)
    continue_btn = wait.until(ec.element_to_be_clickable(CONTINUE_BTN_LOCATOR))
    continue_btn.click()


def contact_info_handler(
    driver,
):
    try:
        first_name = driver.find_element(
            *CONTACT_FORM_FIRST_NAME_LOCATOR
        ).get_attribute("value")
        last_name = driver.find_element(*CONTACT_FORM_LAST_NAME_LOCATOR).get_attribute(
            "value"
        )
        continue_btn = driver.find_element(*CONTINUE_BTN_LOCATOR)

        if all(
            [
                first_name,
                last_name,
                continue_btn.is_enabled(),
            ]
        ):
            return next_step(driver)

        raise MissingInfoError()

    except NoSuchElementException:
        raise MissingInfoError()


url_handler_map = {
    "work-experience": (next_step,),
    "contact-info": (contact_info_handler,),
    "resume": (next_step,),
    "documents": (next_step,),
    "intervention": (next_step,),
    "review": (next_step,),
}


def handle_step(driver: webdriver.Chrome, step):
    try:
        handler, *args = url_handler_map[step]
        return handler(driver, *args)

    except KeyError:
        logger.error("Can't handle current step. No sufficient info. Skipping.")
        raise MissingInfoError()


def apply_in(driver: webdriver.Chrome):
    try:
        apply_btn = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable(APPLY_BTN_LOCATOR)
        )
        apply_btn.click()
    except TimeoutException:
        raise MustApplyOnCompanySiteError()

    try:
        stepper = driver.find_element(*STEPPER_LOCATOR)
    except NoSuchElementException:
        raise NoStepperFoundError()

    text = stepper.text.strip()
    match = re.match(STEPPER_PATTERN, text)

    if not match:
        logger.error(f"Strange error occurred during applying to: {driver.current_url}")
        return None

    count = int(match.group("count")) + 1
    logger.info(f"Found {count} steps.")

    if count > len(url_handler_map):
        raise MissingInfoError()

    for _ in range(count):
        current_step = driver.current_url.split("/")[-1]
        handle_step(driver, current_step)
        time.sleep(5)


def remove_job_alert_overlay(driver: webdriver.Chrome):
    driver.execute_script(
        """
        const bg = document.getElementById('popover-background');
        if (bg) bg.remove();

        const fg = document.getElementById('popover-foreground');
        if (fg) fg.remove();
    """
    )


def get_by_many_possible_locators(driver, locators):
    for locator in locators:
        elements = driver.find_elements(*locator)

        if elements:
            return elements


def close_all_but_first(driver):
    first_handle = driver.window_handles[0]

    for handle in driver.window_handles:
        if handle != first_handle:
            switch_to_tab(driver, handle)
            driver.close()


# Template method pattern
class SiteAutomationProcedure:
    def __init__(self, *args, **kwargs):
        self.uses_2fa = None
        self.args = args
        self.kwargs = kwargs

    def navigate_to_login_page(self):
        pass

    def login(self, email, password):
        pass

    def get_2fa_form(self):
        pass

    def handle_overlays(self):
        pass

    def handle_recommending_different_region(self):
        pass

    def on_code(self, form, code):
        pass

    def start(self, *args, **kwargs):
        pass


async def resolve_func(func):
    if iscoroutinefunction(func):
        code = await func()
    else:
        code = func()

    return code


# TemplateMethod
class IndeedAutomationProcedure(SiteAutomationProcedure):
    def __init__(self, driver, *args, **kwargs):
        self.driver = driver
        super().__init__(**kwargs)

    def navigate_to_login_page(self):
        self.driver.get(INDEED_LOGIN_URL)

    def login(self, email, password):
        form = self.driver.find_element(*LOGIN_FORM_LOCATOR)
        email_input = form.find_element(*EMAIL_INPUT_LOCATOR)
        password_input = form.find_element(*PASSWORD_INPUT_LOCATOR)
        login_btn = form.find_element(*LOGIN_BTN_LOCATOR)

        clear_input(email_input)
        email_input.send_keys(email)

        clear_input(password_input)
        password_input.send_keys(password)

        login_btn.click()

    def get_2fa_form(self):
        try:
            form = self.driver.find_element(*TWO_FACTOR_FORM_LOCATOR)
        except NoSuchElementException:
            form = None

        return form

    def on_code(self, form, code):
        try:
            form_input = form.find_element(*TWO_FACTOR_INPUT_LOCATOR)
            form_input.send_keys(code)
            form.find_element_by_tag_name("button").click()
        except NoSuchElementException:
            raise

    def handle_recommending_different_region(self):
        try:
            invalid_location_anchor = self.driver.find_element_by_class_name(
                "invalid_location"
            ).find_element_by_tag_name("a")
            invalid_location_anchor.click()
        except NoSuchElementException:
            logger.info("No regional restrictions found.")

    def job_search(self, what, where):
        form = self.driver.find_element(*WHAT_WHERE_FORM_LOCATOR)
        what_input = form.find_element(*WHAT_INPUT_LOCATOR)
        where_input = form.find_element(*WHERE_INPUT_LOCATOR)
        find_btn = form.find_element_by_tag_name("button")

        clear_input(what_input)
        what_input.send_keys(what)

        clear_input(where_input)
        where_input.send_keys(where)

        find_btn.click()

    def filter(self):
        filter_by = filters_manager(self.driver)
        filter_by(WithinDistance.OF_100_MILES)

    def handle_overlays(self):
        self.driver.execute_script(
            """
               const bg = document.getElementById('popover-background');
               if (bg) bg.remove();

               const fg = document.getElementById('popover-foreground');
               if (fg) fg.remove();
           """
        )

    async def start(
        self, email, password, what, where, get_2fa_code=None, *args, **kwargs
    ):
        navigate_to_page = paginated_search_manager(self.driver, what, where)
        total_tabs = 16  # 15 per page + 1

        self.navigate_to_login_page()
        self.login(email, password)

        form_2fa = self.get_2fa_form()
        if form_2fa and get_2fa_code:
            code = await resolve_func(get_2fa_code)
            self.on_code(form_2fa, code)

        self.job_search(what, where)
        self.handle_recommending_different_region()

        for current_page in range(1, total_tabs):
            navigate_to_page(current_page)
            self.handle_overlays()
            self.filter()

            job_cards = get_by_many_possible_locators(self.driver, JOB_CARD_LOCATORS)

            for job_card in job_cards:
                if job_card.get_property("tagName").lower() == "a":
                    href = job_card.get_attribute("href")
                else:
                    href = (
                        job_card.find_element_by_tag_name("h2")
                        .find_element_by_tag_name("a")
                        .get_attribute("href")
                    )

                open_in_new_tab(self.driver, href)

            for handle in self.driver.window_handles:
                if handle == self.driver.window_handles[0]:
                    continue

                switch_to_tab(self.driver, handle)

                try:
                    logger.info("Trying to apply for a job.")
                    apply_in(self.driver)
                    logger.info("Applied successfully to a job.")

                except MustApplyOnCompanySiteError:
                    logger.error("Must apply on company site.")

                except MissingInfoError:
                    logger.info("Missing info required to fill in the job form.")

                except NoStepperFoundError:
                    logger.error("Unable to apply to the current job.")

                tabs_count = len(self.driver.window_handles)
                current_handle_index = self.driver.window_handles.index(handle)
                next_handle = self.driver.window_handles[current_handle_index - 1]
                self.driver.close()
                WebDriverWait(self.driver, 5).until(
                    ec.number_of_windows_to_be(tabs_count - 1)
                )
                switch_to_tab(self.driver, next_handle)


if __name__ == "__main__":
    import asyncio

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--email", "-e", metavar="email", dest="email")
    arg_parser.add_argument("--pwd", "-p", metavar="password", dest="password")
    arg_parser.add_argument("--what", "-wt", metavar="what", dest="what")
    arg_parser.add_argument("--where", "-wr", metavar="where", dest="where")
    args = arg_parser.parse_args()

    assert all(
        [args.email, args.password, args.what, args.where]
    ), "You didn't provide all the necessary fields."

    def start_as_script():
        driver = setup_webdriver()
        procedure = IndeedAutomationProcedure(driver)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            procedure.start(
                args.email,
                args.password,
                args.what,
                args.where,
                lambda: input("Enter the code you'll receive on your mail shortly: "),
            )
        )

    start_as_script()
