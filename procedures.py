from collections.abc import Callable


class SiteAutomationProcedure:
    def __init__(self, *args, **kwargs):
        self.uses_2fa = None
        self.args = args
        self.kwargs = kwargs

    async def navigate_to_login_page(self):
        pass

    def get_paginator(self, *args, **kwargs) -> Callable:
        pass

    async def get_2fa_code(self, *args, **kwargs):
        pass

    async def scrap(self, *args, **kwargs):
        pass

    async def start(self, email=None, password=None, *args, **kwargs):
        await self.navigate_to_login_page()
        await self.login(email, password)

        form_2fa = self.get_2fa_form()
        if form_2fa:
            code = self.get_2fa_code(*args, **kwargs)
            self.on_code(form_2fa, code)

        await self.navigate_to_scraping_page(*args, **kwargs)
        await self.scrap(*args, **kwargs)

    async def login(self, email, password):
        pass

    def get_2fa_form(self):
        pass

    def handle_overlays(self):
        pass

    def handle_recommending_different_region(self):
        pass

    def on_code(self, form, code):
        pass

    async def navigate_to_scraping_page(self, *args, **kwargs):
        pass
