from collections.abc import Callable

from consts import EG_INDEED_LOGIN_URL, EG_INDEED_URL
from procedures import SiteAutomationProcedure


class IndeedEGAutomationProcedure(SiteAutomationProcedure):
    def __init__(self, driver, *args, **kwargs):
        self.driver = driver
        super().__init__(**kwargs)

    def navigate_to_login_page(self):
        self.driver.get(EG_INDEED_LOGIN_URL)

    async def login(self, email, password):
        """
        handle logging in
        :param email:
        :param password:
        :return:
        """

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
