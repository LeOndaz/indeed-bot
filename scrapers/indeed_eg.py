from collections.abc import Callable
import asyncio
from selenium.common.exceptions import NoSuchElementException
from consts import EG_INDEED_LOGIN_URL, EG_INDEED_URL
from procedures import SiteAutomationProcedure
from utils import (
    clear_input,
    get_by_many_possible_locators,
    handle_step,
    logger,
    open_in_new_tab,
    paginated_search_manager,
    resolve_func,
    switch_to_tab,
)
from locators_eg import (
    PASSWORD_INPUT_LOCATOR,
    LOGIN_BTN_LOCATOR,
    PASSWORD_FORM_LOCATOR,
    LOGIN_WITH_PASSWORD_URL_LOCATOR,
    EMAIL_BTN_LOCATOR,
    EMAIL_INPUT_LOCATOR,
    EMAIL_FORM_LOCATOR,
    CAPTCHA_CHECK_BOX_LOCATOR
)
class IndeedEGAutomationProcedure(SiteAutomationProcedure):
    def __init__(self, driver, *args, **kwargs):
        self.driver = driver
        super().__init__(**kwargs)

    async def navigate_to_login_page(self):
        self.driver.get(EG_INDEED_LOGIN_URL)

    async def login(self, email, password):
        """
        handle logging in
        :param email:
        :param password:
        :return:
        """
        #fill email form
        email_form = self.driver.find_element(*EMAIL_FORM_LOCATOR)
        email_input = email_form.find_element(*EMAIL_INPUT_LOCATOR)
        email_btn = email_form.find_element(*EMAIL_BTN_LOCATOR)

        clear_input(email_input)
        email_input.send_keys(email)
        email_btn.click()
        # wait for 
        await asyncio.sleep(5)
        captcha_check_boxes = self.driver.find_elements(*CAPTCHA_CHECK_BOX_LOCATOR)
        if captcha_check_boxes:
            captcha_check_box = captcha_check_boxes[0]
            captcha_check_box.click()
            await asyncio.sleep(5)
            email_btn.click()

        # activate login with password
        login_with_password_url = self.driver.find_element(*LOGIN_WITH_PASSWORD_URL_LOCATOR)
        login_with_password_url.click()
        # fill password form
        password_form = self.driver.find_element(*PASSWORD_FORM_LOCATOR)
        password_input = password_form.find_element(*PASSWORD_INPUT_LOCATOR)
        login_btn = password_form.find_element(*LOGIN_BTN_LOCATOR)
        clear_input(password_input)
        password_input.send_keys(password)

        login_btn.click()



    def get_2fa_code(self, *args, **kwargs):
        # handle taking the code from the user
        return input("Enter your code")

    def get_2fa_form(self):
        """
        return place to enter code
        :return:
        """
        return

    def on_code(self, form, code):
        """do logic after code"""

    def handle_overlays(self):
        """handle any overlays"""

    def handle_recommending_different_region(self):
        """handle different regions"""

    async def scrap(self, *args, **kwargs):
        """scraping logic"""

    def get_paginator(self, *args, **kwargs) -> Callable:
        """
        return a function that goes to page

        def func(n):
            "navigate to page"

        :param args:
        :param kwargs:
        :return:
        """

        def func():
            return

        return func

    async def navigate_to_scraping_page(self, *args, **kwargs):
        """
        Go to the page where all magic happens
        :param args:
        :param kwargs:
        :return:
        """
