import argparse
import logging
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse, urlencode
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from consts import (
    INDEED_LOGIN_URL,
    WEB_DRIVER_PATH,
    LOGIN_BTN_LOCATOR,
    LOGIN_FORM_LOCATOR,
    PASSWORD_INPUT_LOCATOR,
    EMAIL_INPUT_LOCATOR,
    WHAT_WHERE_FORM_LOCATOR,
    WHERE_INPUT_LOCATOR,
    WHAT_INPUT_LOCATOR,
    FILTERS_INPUT_LOCATOR,
    JOB_CARD_LOCATORS,
    APPLY_BTN_LOCATOR,
    CONTINUE_BTN_LOCATOR,
    STEPPER_LOCATOR,
    TWO_FACTOR_FORM_LOCATOR,
    TWO_FACTOR_INPUT_LOCATOR,
    ua,
    WithinDistance,
    STEPPER_PATTERN,
)
from errors import (
    MissingInfoError,
    NonExistentPageError
)

logger = logging.getLogger(__file__)


def check_file_existence(file_path):
    return Path(file_path).resolve().exists()


def setup_webdriver():
    """
    Init a new webdriver changing user-agent every time..
    :return:
    """
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={ua.random}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # enable proxy-ing
    # options.add_argument('--proxy-server=209.127.191.180:9279')

    # save profile data
    # options.add_argument(f"user-data-dir={PROFILE_PATH}")

    driver = webdriver.Chrome(executable_path=WEB_DRIVER_PATH, options=options)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def navigate_to_indeed_login_page(driver: webdriver.Chrome):
    driver.get(INDEED_LOGIN_URL)


def open_in_new_tab(driver: webdriver.Chrome, url: str):
    driver.execute_script(f"window.open('{url}', '_blank')")


def switch_to_tab(driver: webdriver.Chrome, tab_num):
    """
    Switches to an active tab.
    :param driver: Driver to act on.
    :param tab_num: Tab number, 0-indexed.
    :return: None
    """
    driver.switch_to.window(driver.window_handles[tab_num])


def clear_input(input):
    input.get_attribute('value')
    input.send_keys(Keys.CONTROL + 'A' + Keys.DELETE)


def filters_manager(driver):
    filters_list = driver.find_element(*FILTERS_INPUT_LOCATOR)

    def filter_by(val_enum):
        filter_element = filters_list.find_element(*val_enum.BTN_LOCATOR.value)
        filter_element.find_element_by_tag_name('button').click()
        anchor = filter_element.find_element(*val_enum.value)
        anchor.click()

    return filter_by


def paginated_search_manager(driver: webdriver.Chrome, what, where):
    """
    1-Indexed.
    :param location:
    :param query:
    :param driver:
    :return:
    """

    def switch_to(page_num):
        parsed_url = list(urlparse(driver.current_url))
        qs = parse_qs(parsed_url[4])
        qs['start'] = (page_num - 1) * 10

        if qs.get('query', None) is not None:
            qs['q'] = what

        if qs.get('location', None) is not None:
            qs['l'] = where

        qs = urlencode(qs)
        parsed_url[4] = qs
        new_url = urlunparse(parsed_url)

        return driver.get(new_url)

    return switch_to


def handle_current_step(driver: webdriver.Chrome):
    def next_step():
        continue_btn = driver.find_element(*CONTINUE_BTN_LOCATOR)
        continue_btn.click()

    def on_missing_contact_info():
        raise MissingInfoError()

    url_handler_map = {
        'contact-info': (on_missing_contact_info,),
        'resume': (next_step,),
        'work-experience': (next_step,),
        'documents': (next_step,),
        'review': (next_step,)
    }
    url_end = driver.current_url.split('/')[-1]

    try:
        handler, *args = url_handler_map[url_end]
        return handler(*args)

    except KeyError:
        logging.warning('Can\'t handle current step. No sufficient info. Skipping.')
        raise MissingInfoError()


def apply_in(driver: webdriver.Chrome):
    apply_btn = driver.find_element(*APPLY_BTN_LOCATOR)
    apply_btn.click()

    stepper = driver.find_element(*STEPPER_LOCATOR)
    text = stepper.get_property('innerText').strip()
    match = re.match(STEPPER_PATTERN, text)

    if match:
        count = int(match.group('count'))
        logging.info(f'Found {count} steps.')

        for _ in range(count + 1):  # review step is added
            handle_current_step(driver)


def remove_job_alert_overlay(driver: webdriver.Chrome):
    driver.execute_script("""
        document.getElementById('popover-background').remove();
        document.getElementById('popover-foreground').remove();
    """)


def close_current_tab(driver: webdriver.Chrome):
    driver.execute_script("""
        window.close();
    """)


def get_many_with_possible_locators(driver, locators):
    for locator in locators:
        elements = driver.find_elements(*locator)

        if elements:
            return elements


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--email', '-e', metavar='email', dest='email')
    arg_parser.add_argument('--pwd', '-p', metavar='password', dest='password')
    arg_parser.add_argument('--what', '-wt', metavar='what', dest='what')
    arg_parser.add_argument('--where', '-wr', metavar='where', dest='where')
    args = arg_parser.parse_args()

    assert all([args.email, args.password, args.what, args.where]), 'You didn\'t provide all the necessary fields.'


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

    def on_code(self, code):
        pass

    def start(self, *args, **kwargs):
        pass


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
            self.uses_2fa = True
        except NoSuchElementException:
            form = None

        return form

    def on_code(self, code):
        form = self.get_2fa_form()
        if form:
            try:
                form_input = form.find_element(*TWO_FACTOR_INPUT_LOCATOR)
                form_input.send_keys(code)
                form.find_element_by_tag_name('button').click()
            except NoSuchElementException:
                raise

    def handle_recommending_different_region(self):
        try:
            invalid_location_anchor = self.driver.find_element_by_class_name(
                'invalid_location').find_element_by_tag_name(
                'a')
            invalid_location_anchor.click()
        except NoSuchElementException:
            logging.info('No regional restrictions found.')

    def job_search(self, what, where):
        form = self.driver.find_element(*WHAT_WHERE_FORM_LOCATOR)
        what_input = form.find_element(*WHAT_INPUT_LOCATOR)
        where_input = form.find_element(*WHERE_INPUT_LOCATOR)
        find_btn = form.find_element_by_tag_name('button')

        clear_input(what_input)
        what_input.send_keys(what)

        clear_input(where_input)
        where_input.send_keys(where)

        find_btn.click()

    async def start(self, email, password, what, where, get_2fa_code=None, *args, **kwargs):
        navigate_to_page = paginated_search_manager(self.driver, what, where)
        current_page = 1

        self.navigate_to_login_page()
        self.login(email, password)

        if get_2fa_code:
            code = await get_2fa_code()
            self.on_code(code)

        self.job_search(what, where)
        self.handle_recommending_different_region()

        filter_by = filters_manager(self.driver)
        filter_by(WithinDistance.OF_100_MILES)

        while True:
            navigate_to_page(current_page)
            current_page += 1
            job_cards = get_many_with_possible_locators(self.driver, JOB_CARD_LOCATORS)

            for job_card in job_cards:
                if job_card.get_property('tagName').lower() == 'a':
                    href = job_card.get_attribute('href')
                else:
                    href = job_card.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')

                open_in_new_tab(self.driver, href)

            total_tabs = 15 + 1
            for i in range(1, total_tabs):
                try:
                    apply_in(self.driver)

                except (MissingInfoError, NoSuchElementException):
                    pass

                switch_to_tab(self.driver, i)

# def start_applying_procedure(id, get_2fa_code, email, password, what, where):
#     driver = setup_webdriver()
#     procedure = IndeedAutomationProcedure(driver, id=id)
#     procedure.start(email, password, what, where, get_2fa_code=get_2fa_code)
