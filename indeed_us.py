import argparse
import logging
import re
import time
from inspect import iscoroutinefunction
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


from errors import MissingInfoError, MustApplyOnCompanySiteError, NoStepperFoundError

from locators_us import (
    APPLY_BTN_LOCATOR,
    CONTACT_FORM_FIRST_NAME_LOCATOR,
    CONTACT_FORM_LAST_NAME_LOCATOR,
    CONTINUE_BTN_LOCATOR,
    EMAIL_INPUT_LOCATOR,
    FILTERS_INPUT_LOCATOR,
    JOB_CARD_LOCATORS,
    LOGIN_BTN_LOCATOR,
    LOGIN_FORM_LOCATOR,
    PASSWORD_INPUT_LOCATOR,
    STEPPER_LOCATOR,

    TWO_FACTOR_FORM_LOCATOR,
    TWO_FACTOR_INPUT_LOCATOR,
    WHAT_INPUT_LOCATOR,
    WHAT_WHERE_FORM_LOCATOR,
    WHERE_INPUT_LOCATOR,
    WithinDistance,
)
from indeed import (
    SiteAutomationProcedure,
    clear_input,
    logger,
    filters_manager,
    paginated_search_manager,
    get_by_many_possible_locators,
    resolve_func,
    apply_in,
    switch_to_tab,
    open_in_new_tab
    )
from consts import (
    US_INDEED_LOGIN_URL as INDEED_LOGIN_URL,
    STEPPER_PATTERN,
    WEB_DRIVER_PATH,
    ua,
)
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